import bpy
import blf
from collections import deque
from dataclasses import dataclass, field
from typing import Literal
import time

from ...lib.editor.editor import is_sn_editor


# Configuration
MAX_ENTRIES = 50
MAX_VISIBLE = 20
EXPIRE_SECONDS = 10.0
FADE_DURATION = 2.0
PADDING = (15, 40)  # x, y from edges

# Use a global namespace to ensure all module instances share the same state
# This fixes the issue where the module gets loaded multiple times
_GLOBAL_KEY = "_sn_log_overlay_state"


@dataclass
class LogEntry:
    level: Literal["INFO", "WARNING", "ERROR"]
    message: str
    timestamp: float = field(default_factory=time.time)
    count: int = 1  # For deduplication


def _get_state():
    """Get the shared state dict from bpy.app.driver_namespace."""
    if _GLOBAL_KEY not in bpy.app.driver_namespace:
        bpy.app.driver_namespace[_GLOBAL_KEY] = {
            "entries": deque(maxlen=MAX_ENTRIES),
            "timer_running": False,
        }
    return bpy.app.driver_namespace[_GLOBAL_KEY]


# Module-level draw handler (not shared - each module instance registers its own)
_draw_handler = None

# Colors per level
COLORS = {
    "INFO": (1.0, 1.0, 1.0, 0.9),
    "WARNING": (1.0, 0.8, 0.2, 0.9),
    "ERROR": (1.0, 0.3, 0.3, 0.9),
}
SHADOW_COLOR = (0.0, 0.0, 0.0, 0.6)


def add_log(level: Literal["INFO", "WARNING", "ERROR"], message: str):
    """Add a log entry to the overlay, deduplicating consecutive identical messages."""
    state = _get_state()
    entries = state["entries"]

    # Deduplicate: if same level and message as the last entry, increment count
    if entries and entries[-1].level == level and entries[-1].message == message:
        # Update timestamp to keep it visible longer and increment count
        entries[-1].timestamp = time.time()
        entries[-1].count += 1
    else:
        entries.append(LogEntry(level, message))

    _start_timer()
    try:
        _redraw_editors()
    except Exception:
        pass  # May fail if called from background thread


def clear_logs():
    """Clear all log entries."""
    _get_state()["entries"].clear()


def _redraw_editors():
    """Request redraw of all node editors."""
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "NODE_EDITOR":
                area.tag_redraw()


def _timer_tick():
    """Timer callback for smooth animation."""
    state = _get_state()

    try:
        if not bpy.context.scene.sna.dev.show_log_overlay:
            state["timer_running"] = False
            return None
    except (AttributeError, KeyError):
        state["timer_running"] = False
        return None

    # Auto-stop timer when no visible entries remain
    entries = state["entries"]
    now = time.time()
    has_visible = any(now - e.timestamp < EXPIRE_SECONDS for e in entries)
    if not has_visible:
        state["timer_running"] = False
        return None

    _redraw_editors()
    return 0.05


def _start_timer():
    """Start the redraw timer if not running."""
    state = _get_state()
    if not state["timer_running"]:
        state["timer_running"] = True
        try:
            bpy.app.timers.register(_timer_tick, first_interval=0.05)
        except Exception:
            state["timer_running"] = False


def _stop_timer():
    """Stop the redraw timer."""
    state = _get_state()
    if state["timer_running"]:
        try:
            bpy.app.timers.unregister(_timer_tick)
        except ValueError:
            pass
        state["timer_running"] = False


def _draw_text_with_shadow(text: str, x: float, y: float, color: tuple, fade: float):
    """Draw text with a shadow for better readability."""
    # Shadow (offset by 1 pixel)
    r, g, b, a = SHADOW_COLOR
    blf.color(0, r, g, b, a * fade)
    blf.position(0, x + 1, y - 1, 0)
    blf.draw(0, text)

    # Main text
    r, g, b, a = color
    blf.color(0, r, g, b, a * fade)
    blf.position(0, x, y, 0)
    blf.draw(0, text)


def _draw_overlay():
    """Draw handler callback."""
    ctx = bpy.context
    if not ctx.area or ctx.area.type != "NODE_EDITOR":
        return

    # Only draw in scripting node editors
    if not is_sn_editor(ctx):
        return

    # Check settings - default to showing if we can't access them
    try:
        dev = ctx.scene.sna.dev
        if not dev.show_log_overlay:
            return
        font_size = dev.log_overlay_font_size
    except (AttributeError, KeyError):
        font_size = 18  # Default if settings not available

    entries = _get_state()["entries"]
    now = time.time()
    visible = [e for e in entries if now - e.timestamp < EXPIRE_SECONDS][-MAX_VISIBLE:]
    if not visible:
        return

    region = ctx.region
    if not region:
        return

    blf.size(0, font_size)
    line_height = int(font_size * 1.3)
    x, y = PADDING[0], region.height - PADDING[1]

    for entry in visible:
        age = now - entry.timestamp
        fade = (
            min(1.0, (EXPIRE_SECONDS - age) / FADE_DURATION)
            if age > EXPIRE_SECONDS - FADE_DURATION
            else 1.0
        )
        color = COLORS.get(entry.level, COLORS["INFO"])

        # Format message with count if duplicated
        if entry.count > 1:
            text = f"[{entry.level}] {entry.message} (x{entry.count})"
        else:
            text = f"[{entry.level}] {entry.message}"

        _draw_text_with_shadow(text, x, y, color, fade)
        y -= line_height


def register():
    global _draw_handler
    _draw_handler = bpy.types.SpaceNodeEditor.draw_handler_add(
        _draw_overlay, (), "WINDOW", "POST_PIXEL"
    )


def unregister():
    global _draw_handler
    _stop_timer()
    if _draw_handler:
        bpy.types.SpaceNodeEditor.draw_handler_remove(_draw_handler, "WINDOW")
        _draw_handler = None
    _get_state()["entries"].clear()
