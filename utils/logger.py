from typing import Any, Literal

import bpy


class bcolors:
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


def log(level: Literal[1, 2, 3, 4], *args: Any):
    """Logs the given message to the console with the given level."""
    # if bpy.context.scene.sna.dev_logs:  # TODO
    color = bcolors.OKBLUE
    if level == 1:
        color = bcolors.OKCYAN
    elif level == 2:
        color = bcolors.OKGREEN
    elif level == 3:
        color = bcolors.WARNING
    elif level == 4:
        color = bcolors.FAIL
    print(f"{color}SN LOG: {bcolors.ENDC}", *args)


def error(*args: Any):
    """Logs the given message to the console as an error."""
    log(4, *args)


def warning(*args: Any):
    """Logs the given message to the console as a warning."""
    log(3, *args)


def success(*args: Any):
    """Logs the given message to the console as success."""
    log(2, *args)


def info(*args: Any):
    """Logs the given message to the console as info."""
    log(1, *args)
