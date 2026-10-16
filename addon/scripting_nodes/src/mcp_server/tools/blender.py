"""Blender in general: run Python, look at the screen, undo, read the log."""

import ast
import contextlib
import io
import os
import tempfile
import traceback

import bpy

from ...settings.preferences import get_preferences
from . import Image, Later, tool
from ._common import ToolError

_OUTPUT_LIMIT = 20000
# variables of run_python, kept between calls
_namespace: dict = {}


def _window():
    windows = bpy.context.window_manager.windows if bpy.context.window_manager else []
    return windows[0] if len(windows) else None


def _area(window, area_type):
    areas = [a for a in window.screen.areas if a.type == area_type]
    if not areas:
        found = sorted({a.type for a in window.screen.areas})
        raise ToolError(f"No {area_type} area on screen. Areas: {found}")
    return max(areas, key=lambda a: a.width * a.height)


def override(area_type=None):
    """Context override for operators that need a window (and an area):
    `with override("VIEW_3D"): bpy.ops.view3d.view_all()`."""
    window = _window()
    if window is None:
        return contextlib.nullcontext()
    if area_type is None:
        return bpy.context.temp_override(window=window, screen=window.screen)
    area = _area(window, area_type)
    region = next((r for r in area.regions if r.type == "WINDOW"), None)
    return bpy.context.temp_override(
        window=window,
        screen=window.screen,
        area=area,
        region=region,
        space_data=area.spaces.active,
    )


def tag_redraw():
    """Have every area drawn (a tool's changes show once Blender gets to it:
    tools that need the drawn result return `Later`)."""
    window = _window()
    if window is not None:
        for area in window.screen.areas:
            area.tag_redraw()


def _fresh_namespace():
    return {"__name__": "__mcp__", "bpy": bpy, "override": override}


@tool(
    "run_python",
    """Run Python in Blender (main thread) and get what it printed, the value
    of the last line (like a console) or the traceback. Variables persist
    between calls. Available: bpy, C (bpy.context), D (bpy.data),
    override(area_type) for operators that need an editor:
    `with override("VIEW_3D"): bpy.ops.view3d.view_all()`. Use it for anything
    the other tools don't cover: scene setup, inspecting data, calling the
    generated add-on's operators. Node trees are better edited with the graph
    tools (they keep ids, links and the build in sync).""",
    {
        "code": {"type": "string", "description": "Python source"},
        "reset": {
            "type": "boolean",
            "description": "Start with fresh variables",
        },
    },
    required=["code"],
    writes=True,
)
def run_python(code, reset=False):
    if not get_preferences().mcp_allow_python:
        raise ToolError(
            "Running Python is turned off (Scripting Nodes preferences, "
            "MCP Server > Allow Running Python)"
        )
    global _namespace
    if reset or not _namespace:
        _namespace = _fresh_namespace()
    _namespace["C"] = bpy.context
    _namespace["D"] = bpy.data
    try:
        tree = ast.parse(code, "<mcp>", "exec")
    except SyntaxError as exc:
        return {"error": f"SyntaxError: {exc}"}
    last = None
    if tree.body and isinstance(tree.body[-1], ast.Expr):
        last = ast.Expression(tree.body.pop().value)
    out = io.StringIO()
    result = {}
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            with override():
                exec(compile(tree, "<mcp>", "exec"), _namespace)
                if last is not None:
                    value = eval(compile(last, "<mcp>", "eval"), _namespace)
                    if value is not None:
                        result["result"] = repr(value)[:_OUTPUT_LIMIT]
    except Exception:  # noqa: BLE001 - the traceback is the answer
        result["error"] = traceback.format_exc(limit=-8)
    printed = out.getvalue()
    if printed:
        result["output"] = printed[-_OUTPUT_LIMIT:]
    return result or {"result": None}


@tool(
    "screenshot",
    """A picture of Blender as the user sees it: the whole window, or the
    biggest area of a type (NODE_EDITOR, VIEW_3D, PROPERTIES, ...). Needs
    Blender with a window (not background mode).""",
    {
        "area": {
            "type": "string",
            "description": "Area type; empty for the whole window",
        },
        "max_size": {
            "type": "integer",
            "description": "Longest side in pixels (default 1600)",
        },
    },
)
def screenshot(area="", max_size=1600):
    if bpy.app.background:
        raise ToolError("Blender runs without a window (background mode)")
    window = _window()
    if window is None:
        raise ToolError("Blender has no window")
    crop = _area(window, area) if area else None
    tag_redraw()
    return Later(lambda: _capture(window, crop, area, max_size))


def _capture(window, crop, area, max_size):
    fd, path = tempfile.mkstemp(suffix=".png", prefix="sn_mcp_")
    os.close(fd)
    try:
        with override():
            tag_redraw()
            bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=1)
            bpy.ops.screen.screenshot(filepath=path, check_existing=False)
        width, height = _shrink(path, max_size, window, crop)
        with open(path, "rb") as f:
            data = f.read()
    finally:
        with contextlib.suppress(OSError):
            os.remove(path)
    areas = ", ".join(sorted({a.type for a in window.screen.areas}))
    return Image(data, text=f"{area or 'Window'} {width}x{height}. Areas: {areas}")


def _shrink(path, max_size, window, area=None):
    """Crop the screenshot at `path` to `area` and scale it down to
    `max_size`, in place. Returns its size."""
    import numpy

    image = bpy.data.images.load(path)
    try:
        image.reload()  # load the pixels now: size is unknown until then
        width, height = image.size
        if area is not None:
            # areas are in their own units (window size or HiDPI pixels)
            extent = max(a.x + a.width for a in window.screen.areas)
            scale = width / extent
            x, y = int(area.x * scale), int(area.y * scale)
            w, h = int(area.width * scale), int(area.height * scale)
            pixels = numpy.empty(width * height * 4, dtype=numpy.float32)
            image.pixels.foreach_get(pixels)
            pixels = pixels.reshape(height, width, 4)[y : y + h, x : x + w]
            cropped = bpy.data.images.new("sn_mcp_crop", w, h, alpha=True)
            cropped.pixels.foreach_set(pixels.ravel())
            bpy.data.images.remove(image)
            image, width, height = cropped, w, h
        factor = max_size / max(width, height, 1)
        if factor < 1:
            width, height = max(1, int(width * factor)), max(1, int(height * factor))
            image.scale(width, height)
        image.filepath_raw = path
        image.file_format = "PNG"
        image.save()
        return width, height
    finally:
        bpy.data.images.remove(image)


@tool(
    "undo",
    """Undo (or redo) the last steps, like Ctrl Z. Every tool that changes
    the file is one step.""",
    {
        "steps": {"type": "integer", "description": "How many (default 1)"},
        "redo": {"type": "boolean", "description": "Redo instead"},
    },
)
def undo(steps=1, redo=False):
    if bpy.app.background:
        raise ToolError("Undo needs Blender with a window")
    done = 0
    with override():
        for _ in range(max(1, steps)):
            operator = bpy.ops.ed.redo if redo else bpy.ops.ed.undo
            if not operator.poll():
                break
            operator()
            done += 1
    return {"steps": done}


@tool(
    "get_logs",
    """Recent messages of Scripting Nodes (errors while building, prints of
    the add-on in the node editor's log).""",
    {"limit": {"type": "integer", "description": "Newest entries (default 50)"}},
)
def get_logs(limit=50):
    state = bpy.app.driver_namespace.get("_sn_log_overlay_state")
    if not state:
        return {"entries": []}
    entries = list(state.get("entries") or [])[-max(1, limit) :]
    return {
        "entries": [
            {"level": e.level, "message": e.message, "count": e.count} for e in entries
        ]
    }
