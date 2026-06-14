"""Marshal MCP tool calls from the HTTP worker thread onto Blender's main
thread.

bpy is not thread-safe. The HTTP server runs in a daemon thread, but every
tool body needs to read/write bpy data — so calls are queued and drained
on the main thread via a `bpy.app.timers` tick. Each call blocks the
worker on a per-request Event until the result (or exception) is set.
"""

from threading import Event
import queue
import traceback
import bpy


_PENDING: "queue.Queue[tuple]" = queue.Queue()
_TIMER_REGISTERED = False
_POLL_INTERVAL = 0.05  # seconds


def _drain():
    """Pump pending callables. Returns the next poll interval (seconds)."""
    while True:
        try:
            fn, args, kwargs, box = _PENDING.get_nowait()
        except queue.Empty:
            break
        try:
            box["result"] = fn(*args, **kwargs)
        except Exception as exc:
            box["error"] = exc
            box["traceback"] = traceback.format_exc()
        finally:
            box["event"].set()
    return _POLL_INTERVAL


def start_pump():
    """Register the main-thread timer. Idempotent."""
    global _TIMER_REGISTERED
    if _TIMER_REGISTERED:
        return
    bpy.app.timers.register(_drain, persistent=True)
    _TIMER_REGISTERED = True


def stop_pump():
    """Unregister the main-thread timer. Idempotent."""
    global _TIMER_REGISTERED
    if not _TIMER_REGISTERED:
        return
    try:
        bpy.app.timers.unregister(_drain)
    except ValueError:
        # Timer was never registered (or was already removed) — ignore.
        pass
    _TIMER_REGISTERED = False


def call_on_main(fn, *args, timeout=10.0, **kwargs):
    """Run `fn(*args, **kwargs)` on Blender's main thread, block, return result.

    Raises whatever `fn` raised, or TimeoutError if the main thread didn't
    pick the call up in time.
    """
    box = {"event": Event()}
    _PENDING.put((fn, args, kwargs, box))
    if not box["event"].wait(timeout=timeout):
        raise TimeoutError(
            f"MCP tool call timed out after {timeout:.1f}s waiting for main thread"
        )
    if "error" in box:
        raise box["error"]
    return box.get("result")
