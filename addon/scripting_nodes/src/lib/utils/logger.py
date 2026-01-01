from typing import Literal


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
        from scripting_nodes.src.handlers.draw.log_overlay import add_log

        add_log(level, message)
    except Exception:
        pass  # May fail during startup/shutdown


def log_if(
    condition: bool, level: Literal["INFO", "WARNING", "ERROR"], *args, **kwargs
):
    if condition:
        log(level, *args, **kwargs)
