"""Shared helper functions of generated addons.

Nodes use them through `ctx.helper(name)`, which returns `utils.<name>`: used
helpers are written to `utils.py` in the generated addon. A helper can behave differently in
the live (dev) addon than in an exported one; this is the only place where
dev and export builds differ, nodes never check the build mode.
"""

import ast
from dataclasses import dataclass

from ..lib.code_format import sort_imports


@dataclass
class Helper:
    # source of the function in dev builds
    dev: str
    # source in exported builds, or None to use `export_name` instead
    export: str | None = None
    # name to call in exported builds instead of importing the helper
    export_name: str | None = None
    # statements run when the add-on is disabled (both builds)
    unregister: str | None = None
    # other helpers this one calls
    requires: tuple = ()


ICON_HELPER = '''
def icon_id(icon):
    """Icon id of a built-in icon's name ("MESH_DATA"), 0 for unknown names.
    Icon ids pass through."""
    if not isinstance(icon, str):
        return icon or 0
    import bpy

    items = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items
    item = items.get(icon)
    return item.value if item else 0
'''

CUSTOM_ICON_HELPER = '''
_previews = None


def custom_icon_id(name):
    """Icon id of the image `icons/<name>` of this add-on (loaded once)."""
    global _previews
    import os

    import bpy.utils.previews

    if _previews is None:
        _previews = bpy.utils.previews.new()
    if name not in _previews:
        path = os.path.join(os.path.dirname(__file__), "icons", name)
        _previews.load(name, path, "IMAGE")
    return _previews[name].icon_id
'''

# UILayout.link is new in Blender 5.2, label_multiline / label_markdown after:
# older versions get a simpler version drawn with labels and buttons
TEXT_HELPERS = '''
def label_multiline(layout, text, max_lines=0, alignment="LEFT", **icon):
    """layout.label_multiline(): text over several lines, wrapped."""
    if hasattr(layout, "label_multiline"):
        layout.label_multiline(
            text=text, max_lines=max_lines, alignment=alignment, **icon
        )
        return
    import textwrap

    import bpy

    region = bpy.context.region
    width = region.width if region else 300
    scale = bpy.context.preferences.system.ui_scale or 1.0
    chars = max(10, int(width / (7 * scale)))
    lines = []
    for paragraph in str(text).splitlines() or [""]:
        lines += textwrap.wrap(paragraph, chars) or [""]
    if max_lines:
        lines = lines[:max_lines]
    has_icon = any(value not in ("NONE", 0) for value in icon.values())
    column = layout.column(align=True)
    column.alignment = alignment
    for i, line in enumerate(lines):
        if i == 0 or not has_icon:
            column.label(text=line, **(icon if i == 0 else {}))
        else:
            column.label(text=line, icon="BLANK1")


def label_markdown(layout, text):
    """layout.label_markdown(): headers, lists, quotes, links, rules."""
    if hasattr(layout, "label_markdown"):
        layout.label_markdown(text=text)
        return
    import re

    column = layout.column()
    for line in str(text).splitlines():
        line = line.strip()
        if re.fullmatch(r"(-{3,}|\\*{3,}|_{3,})", line):
            column.separator(type="LINE")
            continue
        line = re.sub(r"^[-+*]\\s+", "\\u2022 ", line)
        line = re.sub(r"^#{1,6}\\s+", "", line)
        line = re.sub(r"^>\\s?", "    ", line)
        line = re.sub(r"!?\\[([^\\]]*)\\]\\([^)]*\\)", r"\\1", line)
        line = re.sub(r"\\*\\*|\\*|`", "", line)
        if line:
            label_multiline(column, line)
        else:
            column.separator()


def textbox(layout, data, prop, lines=3, placeholder=""):
    """layout.textbox(): a multi-line text field (a normal one before)."""
    if hasattr(layout, "textbox"):
        layout.textbox(
            data, prop, initial_visible_lines=lines, placeholder=placeholder
        )
        return
    layout.prop(data, prop, text="", placeholder=placeholder)


def link(layout, url, text="", **icon):
    """layout.link(): a button opening `url`."""
    if hasattr(layout, "link"):
        layout.link(url=url, text=text, **icon)
        return
    layout.operator("wm.url_open", text=text or url, **icon).url = url
'''


REPORT_HELPER = '''
def report(owner, kind, message):
    """Report a message from an operator (`owner`, shown in the status bar
    and the Info editor), printed where there is none."""
    message = str(message)
    if hasattr(owner, "report"):
        owner.report({kind}, message)
    else:
        log(f"{kind.title()}: {message}")
'''


TIMER_HELPERS = '''
_timers = []


def run_later(function, delay=0.0, persistent=False):
    """Call `function` once after `delay` seconds. Timers stop when the
    add-on is disabled (and when a file is loaded unless `persistent`)."""
    import bpy

    def timer():
        if timer in _timers:
            _timers.remove(timer)
        function()

    _timers.append(timer)
    bpy.app.timers.register(
        timer, first_interval=max(0.0, delay), persistent=persistent
    )


def run_in_intervals(function, interval, times=0, persistent=False):
    """Call `function(index)` every `interval` seconds: `times` times (0: no
    limit) or until it returns False."""
    import bpy

    index = 0

    def timer():
        nonlocal index
        keep_running = function(index)
        index += 1
        if keep_running is False or (times > 0 and index >= times):
            if timer in _timers:
                _timers.remove(timer)
            return None
        return max(0.01, interval)

    _timers.append(timer)
    bpy.app.timers.register(timer, first_interval=0.0, persistent=persistent)
'''

TIMERS_UNREGISTER = """
import bpy

for timer in _timers:
    if bpy.app.timers.is_registered(timer):
        bpy.app.timers.unregister(timer)
_timers.clear()
"""


SHORTCUT_HELPER = '''
_keymaps = []


def add_shortcut(keymap, space_type, idname, key, value="PRESS", properties=None, **modifiers):
    """Add a keymap item to Blender's add-on keyconfig (removed when the
    add-on is disabled)."""
    import bpy

    keyconfig = bpy.context.window_manager.keyconfigs.addon
    if keyconfig is None:  # background mode
        return
    keymap = keyconfig.keymaps.new(name=keymap, space_type=space_type)
    item = keymap.keymap_items.new(idname, key, value, **modifiers)
    for name, prop_value in (properties or {}).items():
        if prop_value is not None:  # keymap items can't hold None
            setattr(item.properties, name, prop_value)
    _keymaps.append((keymap, item))
'''


REDRAW_HELPER = '''
def redraw(area_type=""):
    """Redraw the editors of a type ("VIEW_3D"), all with ""."""
    import bpy

    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if not area_type or area.type == area_type:
                area.tag_redraw()
'''


# Viewport drawing (nodes/categories/drawing): gpu shaders and blf text.
# Points are 2D (pixels, drawing on top) or 3D (the scene), as tuples,
# vectors or lists of them.
DRAW_HANDLER_HELPER = """
_draw_handlers = []


def add_draw_handler(space, function, draw_type):
    \"\"\"Draw `function` in the editors of `space` (bpy.types.SpaceView3D, ...),
    removed when the add-on is disabled.\"\"\"
    handler = space.draw_handler_add(function, (), "WINDOW", draw_type)
    _draw_handlers.append((space, handler))
"""

DRAW_HELPERS = """
def _positions(points):
    return [(p[0], p[1], p[2] if len(p) > 2 else 0.0) for p in points]


def _rgba(color):
    color = tuple(color)
    return color if len(color) == 4 else (*color[:3], 1.0)


def _batch(shader_name, primitive, points, indices=None, **uniforms):
    import gpu
    from gpu_extras.batch import batch_for_shader

    shader = gpu.shader.from_builtin(shader_name)
    batch = batch_for_shader(shader, primitive, {"pos": _positions(points)}, indices=indices)
    shader.bind()
    for name, value in uniforms.items():
        if name == "color":
            value = _rgba(value)
        shader.uniform_float(name, value if isinstance(value, float) else tuple(value))
    batch.draw(shader)


def draw_lines(points, color=(1.0, 1.0, 1.0, 1.0), width=2.0, mode="LINE_STRIP"):
    \"\"\"Lines through `points`: LINE_STRIP connects them, LINE_LOOP closes
    the shape, LINES draws pairs.\"\"\"
    import gpu

    points = list(points)
    if mode == "LINE_LOOP" and points:
        points.append(points[0])
        mode = "LINE_STRIP"
    if len(points) < 2:
        return
    viewport = gpu.state.viewport_get()
    _batch(
        "POLYLINE_UNIFORM_COLOR",
        mode,
        points,
        viewportSize=(viewport[2], viewport[3]),
        lineWidth=float(width),
        color=color,
    )


def draw_points(points, color=(1.0, 1.0, 1.0, 1.0), size=6.0):
    points = list(points)
    if points:
        _batch("POINT_UNIFORM_COLOR", "POINTS", points, color=color, size=float(size))


def draw_polygon(points, color=(1.0, 1.0, 1.0, 1.0)):
    \"\"\"A filled shape with `points` as its outline (also concave ones).\"\"\"
    from mathutils.geometry import tessellate_polygon

    points = _positions(points)
    if len(points) < 3:
        return
    triangles = tessellate_polygon([points])
    _batch("UNIFORM_COLOR", "TRIS", points, indices=triangles, color=color)


def draw_rectangle(position, size, color=(1.0, 1.0, 1.0, 1.0), fill=True, width=2.0):
    \"\"\"A rectangle from its bottom left corner (pixels).\"\"\"
    x, y = position[0], position[1]
    w, h = size[0], size[1]
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    if fill:
        draw_polygon(corners, color)
    else:
        draw_lines(corners, color, width, "LINE_LOOP")


def draw_circle(center, radius, color=(1.0, 1.0, 1.0, 1.0), fill=False, width=2.0,
                segments=32, normal=(0.0, 0.0, 1.0)):
    \"\"\"A circle around `center`, facing `normal` (in 2D: the screen).\"\"\"
    from math import cos, pi, sin

    from mathutils import Vector

    center = Vector(_positions([center])[0])
    axis = Vector(normal).normalized()
    side = axis.orthogonal().normalized()
    up = axis.cross(side)
    points = []
    for i in range(max(3, int(segments))):
        angle = 2 * pi * i / max(3, int(segments))
        points.append(center + (side * cos(angle) + up * sin(angle)) * radius)
    if fill:
        draw_polygon(points, color)
    else:
        draw_lines(points, color, width, "LINE_LOOP")


def draw_text(text, position, size=16.0, color=(1.0, 1.0, 1.0, 1.0), align="LEFT",
              shadow=False):
    \"\"\"Text at `position` (pixels), sized like Blender's interface.\"\"\"
    import blf
    import bpy

    font = 0
    blf.size(font, size * bpy.context.preferences.system.ui_scale)
    width = blf.dimensions(font, str(text))[0]
    x = position[0] - {"LEFT": 0, "CENTER": width / 2, "RIGHT": width}[align]
    blf.position(font, x, position[1], 0)
    blf.color(font, *_rgba(color))
    if shadow:
        blf.enable(font, blf.SHADOW)
        blf.shadow(font, 3, 0.0, 0.0, 0.0, 0.8)
        blf.shadow_offset(font, 1, -1)
    blf.draw(font, str(text))
    if shadow:
        blf.disable(font, blf.SHADOW)


def draw_image(image, position, size, opacity=1.0):
    \"\"\"An image from its bottom left corner (pixels).\"\"\"
    import gpu
    from gpu_extras.batch import batch_for_shader

    if image is None:
        return
    x, y = position[0], position[1]
    w, h = size[0], size[1]
    shader = gpu.shader.from_builtin("IMAGE_COLOR")
    batch = batch_for_shader(
        shader,
        "TRI_FAN",
        {
            "pos": ((x, y, 0), (x + w, y, 0), (x + w, y + h, 0), (x, y + h, 0)),
            "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
        },
    )
    shader.bind()
    shader.uniform_sampler("image", gpu.texture.from_image(image))
    shader.uniform_float("color", (1.0, 1.0, 1.0, float(opacity)))
    batch.draw(shader)


def draw_object(obj, color=(1.0, 1.0, 1.0, 1.0), style="WIRE", width=1.0, size=4.0):
    \"\"\"The evaluated mesh of `obj` (modifiers applied) as wireframe, faces
    or points, where it is in the scene.\"\"\"
    import bpy

    if obj is None:
        return
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    try:
        mesh = evaluated.to_mesh()
    except RuntimeError:  # no geometry (an empty, a light, ...)
        return
    if mesh is None:
        return
    matrix = obj.matrix_world
    points = [matrix @ v.co for v in mesh.vertices]
    if style == "POINTS":
        draw_points(points, color, size)
    elif style == "FACES":
        mesh.calc_loop_triangles()
        triangles = [tuple(t.vertices) for t in mesh.loop_triangles]
        if triangles:
            _batch("UNIFORM_COLOR", "TRIS", points, indices=triangles, color=color)
    else:
        lines = [points[i] for edge in mesh.edges for i in edge.vertices]
        draw_lines(lines, color, width, "LINES")
    evaluated.to_mesh_clear()
"""

# paths starting with // are relative to the .blend file (bpy.path.abspath)
FILE_HELPERS = '''
def read_text(path):
    """The text of a file, "" if it doesn't exist."""
    import os

    import bpy

    path = bpy.path.abspath(path)
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as file:
        return file.read()


def write_text(path, text, append=False):
    """Write text to a file, creating its folder."""
    import os

    import bpy

    path = bpy.path.abspath(path)
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "a" if append else "w", encoding="utf-8") as file:
        file.write(str(text))


def list_folder(folder, extension="", kind="FILES", full_paths=True):
    """Files and/or folders in a folder (sorted), [] if it doesn't exist.
    `extension` filters files (".png", case doesn't matter)."""
    import os

    import bpy

    folder = bpy.path.abspath(folder)
    if not os.path.isdir(folder):
        return []
    found = []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if os.path.isdir(path):
            if kind == "FILES":
                continue
        elif kind == "FOLDERS" or not name.lower().endswith(extension.lower()):
            continue
        found.append(path if full_paths else name)
    return found


def blend_contents(path, data_type):
    """Names of the data of a type ("materials") in a .blend file, sorted."""
    import os

    import bpy

    path = bpy.path.abspath(path)
    if not os.path.isfile(path):
        return []
    with bpy.data.libraries.load(path) as (data_from, _data_to):
        return sorted(getattr(data_from, data_type))


def load_blend(path, data_type, names=None, link=False, add_to_scene=False):
    """Append (or link) data from a .blend file: the given names (a name or
    a list), all with none. Returns the loaded data."""
    import bpy

    if isinstance(names, str):
        names = [names] if names else None
    with bpy.data.libraries.load(bpy.path.abspath(path), link=link) as (
        data_from,
        data_to,
    ):
        available = getattr(data_from, data_type)
        wanted = available if names is None else [n for n in names if n in available]
        setattr(data_to, data_type, list(wanted))
    loaded = [data for data in getattr(data_to, data_type) if data is not None]
    if add_to_scene and data_type in ("objects", "collections"):
        collection = bpy.context.scene.collection
        for data in loaded:
            if data_type == "objects":
                collection.objects.link(data)
            else:
                collection.children.link(data)
    return loaded
'''


MSGBUS_HELPER = '''
from bpy.app.handlers import persistent

_subscriptions = []
_owner = object()


def _subscribe_rna(key, notify):
    import bpy

    bpy.msgbus.subscribe_rna(
        key=key, owner=_owner, args=(), notify=lambda *args: notify()
    )


@persistent
def _resubscribe(*args):
    """Loading a file clears subscriptions."""
    for key, notify in _subscriptions:
        _subscribe_rna(key, notify)


def subscribe(struct, prop, notify):
    """Call `notify()` when `prop` of any `struct` ("Object", "location")
    changes (bpy.msgbus), also after loading another file."""
    import bpy

    key = (getattr(bpy.types, struct), prop)
    _subscriptions.append((key, notify))
    _subscribe_rna(key, notify)
    if _resubscribe not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_resubscribe)
'''


TEXT_HELPER = '''
def as_text(value):
    """A value as text: Blender data (objects, materials, ...) by its name."""
    import bpy

    if isinstance(value, bpy.types.bpy_struct):
        name = getattr(value, "name", None)
        if isinstance(name, str):
            return name
    return str(value)
'''


def _function(source, name):
    """The definition of `name` in `source` (up to the next one)."""
    start = source.index(f"def {name}(")
    end = source.find("\ndef ", start + 1)
    return source[start:] if end == -1 else source[start:end]


# what each drawing helper calls (_positions, _batch are shared)
_DRAW_REQUIRES = {
    "_positions": (),
    "_rgba": (),
    "_batch": ("_positions", "_rgba"),
    "draw_lines": ("_batch",),
    "draw_points": ("_batch",),
    "draw_polygon": ("_batch", "_positions"),
    "draw_rectangle": ("draw_polygon", "draw_lines"),
    "draw_circle": ("draw_polygon", "draw_lines", "_positions"),
    "draw_text": ("_rgba",),
    "draw_image": (),
    "draw_object": ("draw_points", "draw_lines", "_batch"),
}

HELPERS = {
    "log": Helper(
        dev='''
def log(*args):
    """print() that also shows the message in the Scripting Nodes editor."""
    import bpy

    message = " ".join(str(arg) for arg in args)
    print(message)
    overlay = bpy.app.driver_namespace.get("_sn_overlay_log")
    if overlay:
        overlay("INFO", message)
''',
        export_name="print",
    ),
    "icon_id": Helper(dev=ICON_HELPER, export=ICON_HELPER),
    "as_text": Helper(dev=TEXT_HELPER, export=TEXT_HELPER),
    "report": Helper(
        dev=REPORT_HELPER,
        # log is print() in exported add-ons
        export=REPORT_HELPER.replace("log(", "print("),
        requires=("log",),
    ),
    **{
        name: Helper(
            dev=_function(TEXT_HELPERS, name),
            export=_function(TEXT_HELPERS, name),
            requires=("label_multiline",) if name == "label_markdown" else (),
        )
        for name in ("label_multiline", "label_markdown", "link", "textbox")
    },
    "run_later": Helper(
        dev=TIMER_HELPERS[: TIMER_HELPERS.index("def run_in_intervals(")],
        export=TIMER_HELPERS[: TIMER_HELPERS.index("def run_in_intervals(")],
        unregister=TIMERS_UNREGISTER,
    ),
    "run_in_intervals": Helper(
        dev=_function(TIMER_HELPERS, "run_in_intervals"),
        export=_function(TIMER_HELPERS, "run_in_intervals"),
        requires=("run_later",),  # _timers
    ),
    "add_shortcut": Helper(
        dev=SHORTCUT_HELPER,
        export=SHORTCUT_HELPER,
        unregister="""
import contextlib

for keymap, item in _keymaps:
    # gone if Blender removed the keymap already
    with contextlib.suppress(ReferenceError, RuntimeError):
        keymap.keymap_items.remove(item)
_keymaps.clear()
""",
    ),
    "subscribe": Helper(
        dev=MSGBUS_HELPER,
        export=MSGBUS_HELPER,
        unregister="""
import bpy

bpy.msgbus.clear_by_owner(_owner)
if _resubscribe in bpy.app.handlers.load_post:
    bpy.app.handlers.load_post.remove(_resubscribe)
_subscriptions.clear()
""",
    ),
    "redraw": Helper(dev=REDRAW_HELPER, export=REDRAW_HELPER),
    "add_draw_handler": Helper(
        dev=DRAW_HANDLER_HELPER,
        export=DRAW_HANDLER_HELPER,
        unregister="""
for space, handler in _draw_handlers:
    space.draw_handler_remove(handler, "WINDOW")
_draw_handlers.clear()
""",
    ),
    **{
        name: Helper(
            dev=_function(DRAW_HELPERS, name),
            export=_function(DRAW_HELPERS, name),
            requires=_DRAW_REQUIRES[name],
        )
        for name in _DRAW_REQUIRES
    },
    **{
        name: Helper(
            dev=_function(FILE_HELPERS, name), export=_function(FILE_HELPERS, name)
        )
        for name in (
            "read_text",
            "write_text",
            "list_folder",
            "blend_contents",
            "load_blend",
        )
    },
    "custom_icon_id": Helper(
        dev=CUSTOM_ICON_HELPER,
        export=CUSTOM_ICON_HELPER,
        unregister="""
global _previews
if _previews is not None:
    import bpy.utils.previews

    bpy.utils.previews.remove(_previews)
    _previews = None
""",
    ),
}


def source(names, dev: bool) -> str:
    parts = []
    unregister = []
    for name in sorted(names):
        helper = HELPERS[name]
        code = helper.dev if dev else helper.export
        if code:
            parts.append(code.strip() + "\n")
        if helper.unregister:
            unregister.append(helper.unregister.strip())
    if unregister:
        body = "\n".join(unregister)
        parts.append(
            "def unregister():\n"
            + "".join(f"    {line}\n" if line else "\n" for line in body.splitlines())
        )
    code, imports = _hoist_imports("\n\n".join(parts))
    header = '"""Helper functions of the add-on."""\n'
    if imports:
        header += "\n" + "\n".join(sort_imports(imports)) + "\n"
    # isort: one blank line after the imports, two before a definition
    definition = code.startswith(("def ", "class ", "@"))
    return header + ("\n\n" if definition else "\n") + code


def needs_import(name: str, dev: bool) -> bool:
    helper = HELPERS[name]
    return dev or helper.export is not None


def call_name(name: str, dev: bool) -> str:
    helper = HELPERS[name]
    if not dev and helper.export is None and helper.export_name:
        return helper.export_name
    return name


def _hoist_imports(code: str) -> tuple[str, set[str]]:
    """Move the imports of `code` to the top of the module: the helpers are
    written as self-contained functions."""
    tree = ast.parse(code)
    lines = code.split("\n")
    imports, drop = set(), set()
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.Import, ast.ImportFrom))
            and node.lineno == node.end_lineno
        ):
            imports.add(lines[node.lineno - 1].strip())
            drop.add(node.lineno - 1)
            following = node.lineno
            if (
                following < len(lines)
                and not lines[following].strip()
                and node.col_offset
            ):
                drop.add(following)  # the blank line after an import in a function
    kept = [line for i, line in enumerate(lines) if i not in drop]
    return "\n".join(kept).strip("\n") + "\n", imports
