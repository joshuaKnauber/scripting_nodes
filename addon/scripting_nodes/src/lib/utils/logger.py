from typing import Literal


def log(level: Literal["INFO", "WARNING", "ERROR"], *args, **kwargs):
    colors = {
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
    }
    print(colors[level] + f"[SN {level}]", *args, **kwargs)


def log_if(
    condition: bool, level: Literal["INFO", "WARNING", "ERROR"], *args, **kwargs
):
    if condition:
        log(level, *args, **kwargs)
