"""Python-side error state shown in the UI.

Kept out of bpy data on purpose: errors describe the *current* session (a node
whose generate() raised, a generated addon that failed to load) and must never
be restored by undo or saved into the .blend.
"""

import traceback

# node id -> short message
node_errors: dict[str, str] = {}

# Error of the last attempt to load the generated addon (None when it loaded)
addon_error: str | None = None


def set_node_error(node_id: str, exc: BaseException):
    node_errors[node_id] = f"{type(exc).__name__}: {exc}"


def clear_node_error(node_id: str):
    node_errors.pop(node_id, None)


def set_addon_error(message: str | None):
    global addon_error
    addon_error = message


def format_exception(exc: BaseException) -> str:
    return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))


def clear():
    global addon_error
    node_errors.clear()
    addon_error = None
