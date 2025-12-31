import bpy
import blf
from collections import deque
from dataclasses import dataclass, field
from typing import Literal
import time

from scripting_nodes.src.lib.editor.editor import is_sn_editor


# Configuration
MAX_ENTRIES = 50
MAX_VISIBLE = 20
EXPIRE_SECONDS = 10.0
FADE_DURATION = 2.0
PADDING = (15, 40)  # x, y from edges


@dataclass
class LogEntry:
    level: Literal["INFO", "WARNING", "ERROR"]
    message: str
    timestamp: float = field(default_factory=time.time)


# State
_entries: deque[LogEntry] = deque(maxlen=MAX_ENTRIES)
_draw_handler = None
_timer_running = False

# Colors per level
COLORS = {
    "INFO": (1.0, 1.0, 1.0, 0.9),
    "WARNING": (1.0, 0.8, 0.2, 0.9),
    "ERROR": (1.0, 0.3, 0.3, 0.9),
}


def add_log(level: Literal["INFO", "WARNING", "ERROR"], message: str):
    """Add a log entry to the overlay."""
    _entries.append(LogEntry(level, message))
    _start_timer()
    try:
        _redraw_editors()
    except Exception:
        pass  # May fail if called from background thread


def clear_logs():
    """Clear all log entries."""
    _entries.clear()


def _redraw_editors():
    """Request redraw of all node editors."""
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "NODE_EDITOR":
                area.tag_redraw()


def _timer_tick():
    """Timer callback for smooth animation."""
    global _timer_running

    try:
        if not bpy.context.scene.sna.dev.show_log_overlay:
            _timer_running = False
            return None
    except (AttributeError, KeyError):
        _timer_running = False
        return None

    _redraw_editors()
    return 0.05


def _start_timer():
    """Start the redraw timer if not running."""
    global _timer_running
    if not _timer_running:
        _timer_running = True
        try:
            bpy.app.timers.register(_timer_tick, first_interval=0.05)
        except Exception:
            _timer_running = False


def _stop_timer():
    """Stop the redraw timer."""
    global _timer_running
    if _timer_running:
        try:
            bpy.app.timers.unregister(_timer_tick)
        except ValueError:
            pass
        _timer_running = False


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

    now = time.time()
    visible = [e for e in _entries if now - e.timestamp < EXPIRE_SECONDS][-MAX_VISIBLE:]
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
        r, g, b, a = COLORS.get(entry.level, COLORS["INFO"])
        blf.color(0, r, g, b, a * fade)
        blf.position(0, x, y, 0)
        blf.draw(0, f"[{entry.level}] {entry.message}")
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
    _entries.clear()
