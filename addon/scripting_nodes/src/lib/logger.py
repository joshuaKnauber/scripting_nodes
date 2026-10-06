from typing import Callable, Literal

Level = Literal["INFO", "WARNING", "ERROR"]

_COLORS = {
    "INFO": "\033[92m",
    "WARNING": "\033[93m",
    "ERROR": "\033[91m",
}
_RESET = "\033[0m"

# Extra sinks (e.g. the node editor log overlay) register here so the logger
# itself doesn't depend on any UI code.
_listeners: list[Callable[[Level, str], None]] = []


def add_listener(fn: Callable[[Level, str], None]):
    if fn not in _listeners:
        _listeners.append(fn)


def remove_listener(fn: Callable[[Level, str], None]):
    if fn in _listeners:
        _listeners.remove(fn)


def fmt_duration(seconds: float) -> str:
    """Human-friendly duration string."""
    if seconds < 1e-3:
        return f"{seconds * 1e6:.0f}us"
    if seconds < 1:
        return f"{seconds * 1e3:.1f}ms"
    return f"{seconds:.2f}s"


def log(level: Level, *args):
    message = " ".join(str(arg) for arg in args)
    print(f"{_COLORS[level]}[SN {level}]{_RESET} {message}")
    for listener in list(_listeners):
        try:
            listener(level, message)
        except Exception:
            pass  # a broken sink must never break logging


def log_if(condition: bool, level: Level, *args):
    if condition:
        log(level, *args)
