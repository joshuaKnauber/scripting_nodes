from typing import Literal


def fmt_duration(seconds: float) -> str:
    """Human-friendly duration string."""
    if seconds < 1e-3:
        return f"{seconds * 1e6:.0f}us"
    if seconds < 1:
        return f"{seconds * 1e3:.1f}ms"
    return f"{seconds:.2f}s"


def log(level: Literal["INFO", "WARNING", "ERROR"], *args, **kwargs):
    colors = {
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
    }
    message = " ".join(str(arg) for arg in args)
    print(colors[level] + f"[SN {level}]", *args, **kwargs)

    # Also add to overlay
    try:
        from ...handlers.draw.log_overlay import add_log

        add_log(level, message)
    except Exception:
        pass  # May fail during startup/shutdown


def log_if(
    condition: bool, level: Literal["INFO", "WARNING", "ERROR"], *args, **kwargs
):
    if condition:
        log(level, *args, **kwargs)
