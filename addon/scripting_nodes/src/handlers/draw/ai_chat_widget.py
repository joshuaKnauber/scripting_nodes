"""AI Chat widget drawn as a GPU overlay in the node editor.

Always shows a small AI button in the bottom-left of the node editor.
Clicking it expands to a full chat panel. Panel is horizontally
resizable by dragging the right edge.
"""

import bpy
import blf
import gpu
import math
from gpu_extras.batch import batch_for_shader

from ...lib.editor.editor import is_sn_editor
from ...features.ai.generation import (
    is_generating,
    get_generating_node_id,
    start_generation,
    request_stop,
    get_next_response,
)

# ── Layout ────────────────────────────────────────────────────────
BASE_FONT_SIZE = 18
MARGIN = 16
MAX_VISIBLE_MESSAGES = 50
MIN_WIDTH = 320
MAX_WIDTH = 1200
DEFAULT_WIDTH = 800
RESIZE_HANDLE_W = 6

# ── Palette ───────────────────────────────────────────────────────
# Dark, neutral base – all slightly warm so it feels cohesive
COL_BG          = (0.13, 0.13, 0.14, 0.94)
COL_HEADER_BG   = (0.11, 0.11, 0.12, 0.98)
COL_INPUT_BG    = (0.18, 0.18, 0.19, 1.0)
COL_INPUT_FOCUS = (0.22, 0.22, 0.24, 1.0)
COL_INPUT_BORDER = (0.28, 0.28, 0.30, 1.0)
COL_INPUT_BORDER_FOCUS = (0.40, 0.55, 0.90, 0.8)
COL_USER_BG     = (0.18, 0.22, 0.32, 0.85)
COL_ASST_BG     = (0.17, 0.17, 0.18, 0.85)
COL_TEXT        = (0.88, 0.88, 0.90, 1.0)
COL_TEXT_SEC    = (0.55, 0.55, 0.58, 1.0)
COL_ACCENT      = (0.38, 0.56, 0.94, 1.0)
COL_ACCENT_HOVER = (0.48, 0.64, 1.0, 1.0)
COL_STOP        = (0.85, 0.30, 0.30, 1.0)
COL_HINT        = (0.42, 0.42, 0.45, 0.7)
COL_CURSOR      = (0.75, 0.80, 0.95, 1.0)
COL_CLEAR_BG    = (0.20, 0.20, 0.22, 0.6)
COL_CLEAR_TEXT  = (0.60, 0.60, 0.62, 1.0)
COL_SEPARATOR   = (0.22, 0.22, 0.24, 0.6)
COL_SCROLL      = (0.40, 0.40, 0.42, 0.35)
COL_FAB         = (0.30, 0.50, 0.90, 1.0)
COL_FAB_RING    = (0.40, 0.60, 1.0, 0.25)
COL_RESIZE      = (0.35, 0.35, 0.38, 0.0)   # invisible until hover
COL_RESIZE_HOT  = (0.45, 0.55, 0.90, 0.5)

# ── State ─────────────────────────────────────────────────────────
_GLOBAL_KEY = "_sn_ai_chat_widget_state"
_draw_handler = None


def _get_state():
    if _GLOBAL_KEY not in bpy.app.driver_namespace:
        bpy.app.driver_namespace[_GLOBAL_KEY] = {
            "expanded": False,
            "input_focused": False,
            "input_text": "",
            "scroll_offset": -1,
            "modal_running": False,
            "hit_rects": {},
            "_was_generating": False,
            "panel_width": DEFAULT_WIDTH,
            "resizing": False,
            "resize_start_x": 0,
            "resize_start_w": 0,
            "messages": [],
        }
    state = bpy.app.driver_namespace[_GLOBAL_KEY]
    state.setdefault("panel_width", DEFAULT_WIDTH)
    state.setdefault("resizing", False)
    state.setdefault("messages", [])
    return state


def _get_selection_context(context):
    """Build context string and find the active script node (if any)."""
    ntree = getattr(context.space_data, "edit_tree", None) if context.space_data else None
    if not ntree:
        return "", None

    selected = [n for n in ntree.nodes if n.select]
    active = context.active_node
    script_node = None

    if active and getattr(active, "bl_idname", "") == "SNA_Node_Script":
        script_node = active

    parts = []
    if active:
        parts.append(f"Active node: {active.bl_label} ({active.bl_idname})")
    if selected:
        names = [f"{n.bl_label} ({n.bl_idname})" for n in selected if n != active]
        if names:
            parts.append(f"Also selected: {', '.join(names)}")
    if not selected and not active:
        parts.append("No nodes selected.")

    return "\n".join(parts), script_node


def _get_font_size():
    try:
        return bpy.context.scene.sna.dev.log_overlay_font_size
    except (AttributeError, KeyError):
        return BASE_FONT_SIZE


def _s(font_size):
    """Scale factor relative to base font."""
    return font_size / BASE_FONT_SIZE


# ── Drawing primitives ───────────────────────────────────────────

_shader = gpu.shader.from_builtin("UNIFORM_COLOR")


def _rect(x, y, w, h, color):
    verts = ((x, y), (x + w, y), (x + w, y + h), (x, y + h))
    idx = ((0, 1, 2), (0, 2, 3))
    batch = batch_for_shader(_shader, "TRIS", {"pos": verts}, indices=idx)
    _shader.bind()
    _shader.uniform_float("color", color)
    batch.draw(_shader)


def _rect_outline(x, y, w, h, color, thickness=1):
    """Draw a 1px outline rectangle."""
    t = thickness
    _rect(x, y, w, t, color)           # bottom
    _rect(x, y + h - t, w, t, color)   # top
    _rect(x, y, t, h, color)           # left
    _rect(x + w - t, y, t, h, color)   # right


def _text(text, x, y, color=COL_TEXT, size=None):
    blf.size(0, size or BASE_FONT_SIZE)
    blf.color(0, *color)
    blf.position(0, x, y, 0)
    blf.draw(0, text)


def _tw(text, size=None):
    blf.size(0, size or BASE_FONT_SIZE)
    return blf.dimensions(0, text)[0]


def _wrap(text, max_w, size=None):
    blf.size(0, size or BASE_FONT_SIZE)
    out = []
    for para in text.split("\n"):
        if not para.strip():
            out.append("")
            continue
        words = para.split(" ")
        line = ""
        for w in words:
            t = f"{line} {w}".strip()
            if blf.dimensions(0, t)[0] > max_w and line:
                out.append(line)
                line = w
            else:
                line = t
        if line:
            out.append(line)
    return out


def _in(mx, my, r):
    x, y, w, h = r
    return x <= mx <= x + w and y <= my <= y + h


def _redraw():
    for win in bpy.context.window_manager.windows:
        for a in win.screen.areas:
            if a.type == "NODE_EDITOR":
                a.tag_redraw()


# ── FAB button ────────────────────────────────────────────────────

def _draw_fab(region, fs):
    s = _s(fs)
    sz = int(42 * s)
    x, y = MARGIN, MARGIN

    # Shadow
    _rect(x + 2, y - 2, sz, sz, (0.0, 0.0, 0.0, 0.25))
    # Button background
    _rect(x, y, sz, sz, COL_FAB)
    # Accent top edge
    _rect(x, y + sz - 2, sz, 2, COL_ACCENT)

    # Chat bubble icon: small speech bubble shape using rects
    bx = x + sz * 0.25
    by = y + sz * 0.32
    bw = sz * 0.5
    bh = sz * 0.32
    _rect(bx, by, bw, bh, (1, 1, 1, 0.9))
    # Bubble tail
    _rect(bx + bw * 0.15, by - sz * 0.08, sz * 0.1, sz * 0.1, (1, 1, 1, 0.9))
    # Two dots inside bubble to suggest text
    dot = max(2, int(3 * s))
    dot_y = by + bh * 0.4
    _rect(bx + bw * 0.28, dot_y, dot, dot, COL_FAB)
    _rect(bx + bw * 0.55, dot_y, dot, dot, COL_FAB)

    return (x, y, sz, sz)


# ── Chat panel ────────────────────────────────────────────────────

def _draw_panel(region, state, context, fs):
    s = _s(fs)
    ww = max(MIN_WIDTH, min(state["panel_width"], MAX_WIDTH, region.width - MARGIN * 2))
    state["panel_width"] = ww
    pad = int(14 * s)
    lh = int(fs * 1.45)
    ih = int(38 * s)
    hh = int(42 * s)
    ms = int(8 * s)
    btn_w = int(54 * s)
    border = 1

    sel_info, script_node = _get_selection_context(context)
    messages = state["messages"]
    gen = is_generating()
    cw = ww - pad * 2  # content width

    # Determine context label early so we know the header height
    ctx_label = ""
    if script_node:
        if script_node.source_type == "INTERNAL" and script_node.text_block:
            ctx_label = f"Script: {script_node.text_block.name}"
        elif script_node.source_type == "EXTERNAL" and script_node.filepath:
            import os
            ctx_label = f"Script: {os.path.basename(script_node.filepath)}"
        else:
            ctx_label = "Script node (no file)"
    else:
        active = context.active_node
        if active and getattr(active, "is_sn", False):
            ctx_label = f"Selected: {active.bl_label}"

    ctx_bar_h = int(lh * 0.85) if ctx_label else 0
    full_hh = hh + ctx_bar_h

    # Wrap messages
    wrapped = []
    for msg in messages:
        lines = _wrap(msg["content"].strip(), cw - pad * 2, fs)
        h = lh + max(len(lines), 1) * lh + pad
        wrapped.append({"msg": msg, "lines": lines, "h": h})

    vis = wrapped[-MAX_VISIBLE_MESSAGES:]
    msgs_h = sum(e["h"] + ms for e in vis)
    hints_h = lh * 5 + pad if not messages else 0

    # Fixed chrome height (full header + input + padding)
    chrome_h = full_hh + ih + pad * 4
    max_h = int(region.height * 0.75)
    total_h = chrome_h + msgs_h + hints_h
    wx, wy = MARGIN, MARGIN
    wh = max(chrome_h + lh * 3, min(total_h, max_h))

    hit = state["hit_rects"]
    hit["widget"] = (wx, wy, ww, wh)

    # ── Panel background with subtle border ───────────────
    _rect(wx, wy, ww, wh, COL_BG)
    _rect_outline(wx, wy, ww, wh, COL_SEPARATOR)

    # ── Resize handle (right edge) ────────────────────────
    rh_x = wx + ww - RESIZE_HANDLE_W
    hit["resize"] = (rh_x, wy, RESIZE_HANDLE_W * 2, wh)
    if state.get("resizing"):
        _rect(rh_x, wy, RESIZE_HANDLE_W, wh, COL_RESIZE_HOT)

    # ── Header ────────────────────────────────────────────
    hy = wy + wh - full_hh
    _rect(wx, hy, ww, full_hh, COL_HEADER_BG)
    # Separator line below header
    _rect(wx, hy, ww, 1, COL_SEPARATOR)

    # Title row (top of header)
    title_y = hy + ctx_bar_h
    _text("Assistant", wx + pad, title_y + hh // 2 - fs // 2, COL_TEXT, fs)

    # Header buttons (right-aligned): [Clear] [—]
    hbtn_fs = int(fs * 0.78)
    hbtn_h = int(24 * s)
    hbtn_y = title_y + (hh - hbtn_h) // 2
    hbtn_pad = int(10 * s)
    hbtn_gap = int(4 * s)

    # Minimize button
    min_label = "—"
    min_lw = _tw(min_label, int(fs * 0.9))
    min_w = int(min_lw + hbtn_pad * 2)
    min_x = wx + ww - min_w - pad // 2
    _rect(min_x, hbtn_y, min_w, hbtn_h, (0.25, 0.25, 0.27, 0.5))
    _text(min_label, min_x + (min_w - min_lw) / 2, hbtn_y + hbtn_h // 2 - int(fs * 0.9) // 2, COL_TEXT_SEC, int(fs * 0.9))
    hit["minimize"] = (min_x, hbtn_y, min_w, hbtn_h)

    # Clear button (left of minimize)
    if messages and not gen:
        cl_txt = "Clear"
        cl_tw = _tw(cl_txt, hbtn_fs)
        cl_w = int(cl_tw + hbtn_pad * 2)
        cl_x = min_x - cl_w - hbtn_gap
        _rect(cl_x, hbtn_y, cl_w, hbtn_h, COL_CLEAR_BG)
        _text(cl_txt, cl_x + (cl_w - cl_tw) / 2, hbtn_y + hbtn_h // 2 - hbtn_fs // 2, COL_CLEAR_TEXT, hbtn_fs)
        hit["clear"] = (cl_x, hbtn_y, cl_w, hbtn_h)
    else:
        hit.pop("clear", None)

    # Context bar: shows selection state
    if ctx_label:
        ctx_fs = int(fs * 0.75)
        bar_col = COL_ACCENT if script_node else COL_TEXT_SEC
        _rect(wx + pad, hy + int(3 * s), int(2 * s), ctx_bar_h - int(6 * s), bar_col)
        _text(ctx_label, wx + pad + int(8 * s), hy + ctx_bar_h // 2 - ctx_fs // 2, COL_TEXT_SEC, ctx_fs)

    # ── Input area ────────────────────────────────────────
    iy = wy + pad

    # Send/Stop button
    bx = wx + ww - pad - btn_w
    bc = COL_STOP if gen else COL_ACCENT
    _rect(bx, iy, btn_w, ih, bc)
    bl = "Stop" if gen else "Send"
    blw = _tw(bl, fs)
    _text(bl, bx + (btn_w - blw) / 2, iy + ih // 2 - fs // 2, (1, 1, 1, 1), fs)
    hit["send_btn"] = (bx, iy, btn_w, ih)

    # Input field
    iw = cw - btn_w - int(8 * s)
    ix = wx + pad
    ibg = COL_INPUT_FOCUS if state["input_focused"] else COL_INPUT_BG
    ibc = COL_INPUT_BORDER_FOCUS if state["input_focused"] else COL_INPUT_BORDER
    _rect(ix, iy, iw, ih, ibg)
    _rect_outline(ix, iy, iw, ih, ibc)
    hit["input"] = (ix, iy, iw, ih)

    itxt = state["input_text"]
    tx = ix + int(10 * s)
    ty = iy + ih // 2 - fs // 2

    if itxt:
        dt = itxt
        max_tw = iw - int(20 * s)
        while _tw(dt, fs) > max_tw and len(dt) > 1:
            dt = dt[1:]
        _text(dt, tx, ty, COL_TEXT, fs)
        if state["input_focused"]:
            cx = tx + _tw(itxt, fs)
            if cx > ix + iw - int(10 * s):
                cx = tx + _tw(dt, fs)
            _rect(cx + 1, iy + int(6 * s), 2, ih - int(12 * s), COL_CURSOR)
    else:
        _text("Ask the AI...", tx, ty, COL_HINT, fs)
        if state["input_focused"]:
            _rect(tx, iy + int(6 * s), 2, ih - int(12 * s), COL_CURSOR)

    # ── Separator above input ─────────────────────────────
    _rect(wx + pad, iy + ih + int(6 * s), cw, 1, COL_SEPARATOR)

    # ── Messages area ─────────────────────────────────────
    msg_top = hy - pad
    msg_bot = iy + ih + pad + int(8 * s)
    cy = msg_top

    scroll = state["scroll_offset"]

    if not messages:
        ty = cy
        ty -= lh
        _text("Ask the assistant anything:", wx + pad, ty, COL_TEXT_SEC, fs)
        hints = [
            "'How do I use the Panel node?'",
            "'Write a script that adds a cube'",
            "'What does my node setup do?'",
        ]
        for h in hints:
            ty -= lh
            _text("•  " + h, wx + pad + int(6 * s), ty, COL_HINT, fs)
    else:
        tot_h = sum(e["h"] + ms for e in vis)
        avail = max(1, cy - msg_bot)
        max_scr = max(0, tot_h - avail)
        # scroll_offset = -1 means "pin to bottom"
        if scroll < 0:
            scroll = max_scr
        scroll = max(0, min(scroll, max_scr))
        state["scroll_offset"] = scroll
        state["_max_scroll"] = max_scr

        dy = cy + scroll

        for entry in vis:
            msg_data = entry["msg"]
            lines = entry["lines"]
            h = entry["h"]
            dy -= h

            # Skip entirely off-screen entries
            if dy + h < msg_bot:
                dy -= ms
                continue
            if dy > cy:
                dy -= ms
                continue

            is_user = msg_data["role"] == "user"
            bg = COL_USER_BG if is_user else COL_ASST_BG

            # Clip bubble to message area bounds
            draw_y = max(dy, msg_bot)
            draw_h = min(dy + h, cy) - draw_y
            if draw_h <= 0:
                dy -= ms
                continue

            # Message bubble with left accent bar
            _rect(wx + pad, draw_y, cw, draw_h, bg)
            bar_col = COL_ACCENT if not is_user else (0.45, 0.55, 0.70, 0.6)
            _rect(wx + pad, draw_y, int(3 * s), draw_h, bar_col)

            # Role label (only if within bounds)
            label = "You" if is_user else "AI"
            lbl_col = (0.65, 0.70, 0.80, 1.0) if is_user else COL_ACCENT
            lbl_fs = int(fs * 0.82)
            lty = dy + h - lh
            if msg_bot <= lty <= cy:
                _text(label, wx + pad * 2 + int(4 * s), lty, lbl_col, lbl_fs)

            # Message text (only lines within bounds)
            lty -= int(lh * 0.2)
            for line in lines:
                lty -= lh
                if lty < msg_bot - lh:
                    break
                if msg_bot <= lty <= cy:
                    _text(line, wx + pad * 2 + int(4 * s), lty, COL_TEXT, fs)

            dy -= ms

        # Scrollbar
        if max_scr > 0:
            bar_h = max(20, avail * (avail / tot_h))
            bar_y = msg_bot + (avail - bar_h) * (1 - scroll / max_scr)
            _rect(wx + ww - int(5 * s), bar_y, int(3 * s), bar_h, COL_SCROLL)


# ── Main draw ─────────────────────────────────────────────────────

def _draw_widget():
    ctx = bpy.context
    if not ctx.area or ctx.area.type != "NODE_EDITOR":
        return
    if not is_sn_editor(ctx):
        return
    region = ctx.region
    if not region:
        return

    state = _get_state()
    fs = _get_font_size()

    gpu.state.blend_set("ALPHA")

    if state["expanded"]:
        _draw_panel(region, state, ctx, fs)
    else:
        state["hit_rects"]["fab"] = _draw_fab(region, fs)

    gpu.state.blend_set("NONE")

    # Keep modal alive
    _ensure_modal()


def _ensure_modal():
    state = _get_state()
    if state["modal_running"]:
        return
    try:
        bpy.ops.sna.ai_chat_modal("INVOKE_DEFAULT")
    except Exception:
        pass


# ── Modal operator ────────────────────────────────────────────────

class SNA_OT_AIChatModal(bpy.types.Operator):
    bl_idname = "sna.ai_chat_modal"
    bl_label = "AI Chat"
    bl_options = {"INTERNAL"}

    _timer = None

    @classmethod
    def poll(cls, context):
        return context.area and context.area.type == "NODE_EDITOR"

    def invoke(self, context, event):
        state = _get_state()
        if state["modal_running"]:
            return {"CANCELLED"}
        state["modal_running"] = True
        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        self._cleanup(context)

    def _cleanup(self, context):
        state = _get_state()
        state["modal_running"] = False
        state["input_focused"] = False
        state["resizing"] = False
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        try:
            context.window.cursor_set("DEFAULT")
        except Exception:
            pass

    def modal(self, context, event):
        state = _get_state()

        if not context.area or context.area.type != "NODE_EDITOR":
            return {"PASS_THROUGH"}
        if not is_sn_editor(context):
            return {"PASS_THROUGH"}

        hit = state["hit_rects"]
        mx, my = event.mouse_region_x, event.mouse_region_y

        # ── Timer ─────────────────────────────────────────────
        if event.type == "TIMER":
            self._poll_gen(context, state)
            return {"PASS_THROUGH"}

        # ── Early scroll intercept (before node editor can consume it) ──
        if state["expanded"] and event.type in ("WHEELUPMOUSE", "WHEELDOWNMOUSE",
                                                  "TRACKPADZOOM", "TRACKPADPAN"):
            in_w_early = "widget" in hit and _in(mx, my, hit["widget"])
            if in_w_early:
                if event.type == "WHEELUPMOUSE":
                    state["scroll_offset"] += 40
                elif event.type == "WHEELDOWNMOUSE":
                    state["scroll_offset"] = max(0, state["scroll_offset"] - 40)
                elif event.type == "TRACKPADPAN":
                    # event.mouse_prev_y gives the previous position
                    dy = event.mouse_y - event.mouse_prev_y
                    state["scroll_offset"] = max(0, state["scroll_offset"] + int(dy))
                _redraw()
                return {"RUNNING_MODAL"}

        # ── Resize drag ───────────────────────────────────────
        if state.get("resizing"):
            if event.type == "MOUSEMOVE":
                delta = mx - state["resize_start_x"]
                new_w = state["resize_start_w"] + delta
                state["panel_width"] = max(MIN_WIDTH, min(new_w, MAX_WIDTH))
                _redraw()
                return {"RUNNING_MODAL"}
            if event.type == "LEFTMOUSE" and event.value == "RELEASE":
                state["resizing"] = False
                try:
                    context.window.cursor_set("DEFAULT")
                except Exception:
                    pass
                _redraw()
                return {"RUNNING_MODAL"}
            return {"RUNNING_MODAL"}

        # ── Cursor for resize handle ──────────────────────────
        if event.type == "MOUSEMOVE" and state["expanded"] and not state.get("resizing"):
            on_handle = "resize" in hit and _in(mx, my, hit["resize"])
            try:
                if on_handle:
                    context.window.cursor_set("MOVE_X")
                else:
                    context.window.cursor_set("DEFAULT")
            except Exception:
                pass

        # ── FAB click ─────────────────────────────────────────
        if not state["expanded"]:
            if event.type == "LEFTMOUSE" and event.value == "PRESS":
                if "fab" in hit and _in(mx, my, hit["fab"]):
                    state["expanded"] = True
                    state["scroll_offset"] = -1
                    _redraw()
                    return {"RUNNING_MODAL"}
            return {"PASS_THROUGH"}

        # ── Panel interaction ─────────────────────────────────
        in_w = "widget" in hit and _in(mx, my, hit["widget"])

        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            if "resize" in hit and _in(mx, my, hit["resize"]):
                state["resizing"] = True
                state["resize_start_x"] = mx
                state["resize_start_w"] = state["panel_width"]
                return {"RUNNING_MODAL"}

            if not in_w:
                state["input_focused"] = False
                _redraw()
                return {"PASS_THROUGH"}

            if "minimize" in hit and _in(mx, my, hit["minimize"]):
                state["expanded"] = False
                state["input_focused"] = False
                _redraw()
                return {"RUNNING_MODAL"}

            if "send_btn" in hit and _in(mx, my, hit["send_btn"]):
                if is_generating():
                    request_stop()
                else:
                    self._send(context, state)
                _redraw()
                return {"RUNNING_MODAL"}

            if "clear" in hit and _in(mx, my, hit["clear"]):
                state["messages"] = []
                state["scroll_offset"] = -1
                _redraw()
                return {"RUNNING_MODAL"}

            if "input" in hit and _in(mx, my, hit["input"]):
                state["input_focused"] = True
                _redraw()
                return {"RUNNING_MODAL"}

            state["input_focused"] = False
            _redraw()
            return {"RUNNING_MODAL"}

        # Block unhandled mouse events inside the widget
        if in_w and event.type in ("RIGHTMOUSE", "MIDDLEMOUSE", "MOUSEMOVE"):
            return {"RUNNING_MODAL"}

        # Keyboard
        if state["input_focused"] and event.value == "PRESS":
            if event.type == "RET":
                if not is_generating():
                    self._send(context, state)
                _redraw()
                return {"RUNNING_MODAL"}

            if event.type == "ESC":
                if is_generating():
                    request_stop()
                else:
                    state["input_focused"] = False
                _redraw()
                return {"RUNNING_MODAL"}

            if event.type == "BACK_SPACE":
                if state["input_text"]:
                    state["input_text"] = state["input_text"][:-1]
                _redraw()
                return {"RUNNING_MODAL"}

            if event.type == "DEL":
                state["input_text"] = ""
                _redraw()
                return {"RUNNING_MODAL"}

            if event.unicode and event.unicode.isprintable():
                state["input_text"] += event.unicode
                _redraw()
                return {"RUNNING_MODAL"}

            if event.type in ("TAB", "SPACE"):
                if event.type == "SPACE":
                    state["input_text"] += " "
                _redraw()
                return {"RUNNING_MODAL"}

        return {"PASS_THROUGH"}

    def _poll_gen(self, context, state):
        ga = is_generating()
        gw = state.get("_was_generating", False)

        if ga or gw:
            updated = False
            done = False
            for _ in range(100):
                resp, done = get_next_response()
                if resp is not None:
                    msgs = state["messages"]
                    if msgs and msgs[-1]["role"] == "assistant":
                        msgs[-1]["content"] = resp
                    if state["scroll_offset"] < 0 or state["scroll_offset"] >= state.get("_max_scroll", 0) - 5:
                        state["scroll_offset"] = -1
                    updated = True
                if done or (resp is None and not done):
                    break
            if done:
                state["_was_generating"] = False
                msgs = state["messages"]
                if msgs and msgs[-1]["role"] == "assistant" and msgs[-1]["content"] == "...":
                    msgs[-1]["content"] = "(No response received)"
                updated = True
            if updated:
                _redraw()
        state["_was_generating"] = ga

    def _send(self, context, state):
        t = state["input_text"].strip()
        if not t:
            return

        _, script_node = _get_selection_context(context)
        sel_info, _ = _get_selection_context(context)

        msgs = state["messages"]
        msgs.append({"role": "user", "content": t})
        msgs.append({"role": "assistant", "content": "..."})

        state["input_text"] = ""
        state["scroll_offset"] = -1

        start_generation(
            script_node,
            t,
            conversation_history=msgs,
            context_info=sel_info,
        )


# ── Registration ──────────────────────────────────────────────────

def register():
    global _draw_handler
    _draw_handler = bpy.types.SpaceNodeEditor.draw_handler_add(
        _draw_widget, (), "WINDOW", "POST_PIXEL"
    )


def unregister():
    global _draw_handler
    state = _get_state()
    state["expanded"] = False
    state["modal_running"] = False
    state["resizing"] = False
    if _draw_handler:
        bpy.types.SpaceNodeEditor.draw_handler_remove(_draw_handler, "WINDOW")
        _draw_handler = None
