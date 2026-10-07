"""Show exceptions raised by the running generated addon on their node.

Blender prints errors of operators, panels, handlers, ... through
sys.excepthook. While Scripting Nodes is enabled we wrap it: frames inside
the generated addon are mapped back to the node that wrote the line (via the
compiler's line map) and the error is shown on that node. The generated code
itself contains nothing for this.
"""

import os
import sys
import traceback

from ..lib.logger import log
from . import errors

_original = None


def _blame(exc_type, exc, tb):
    from . import runtime
    from .compiler import line_owners

    module = runtime.loaded_module()
    if not module or tb is None:
        return
    root = os.path.realpath(runtime.folder(module))
    node_id = None
    for frame in traceback.extract_tb(tb):
        path = os.path.realpath(frame.filename)
        if not path.startswith(root + os.sep):
            continue
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        owners = line_owners.get(rel, [])
        if (
            frame.lineno
            and 0 < frame.lineno <= len(owners)
            and owners[frame.lineno - 1]
        ):
            node_id = owners[frame.lineno - 1]  # innermost wins
    if node_id is None:
        return
    message = f"{exc_type.__name__}: {exc}"
    errors.runtime_errors[node_id] = message
    from ..lib.trees import node_by_id
    from ..lib.screen import redraw_all

    node = node_by_id(node_id)
    log("ERROR", f"Error in node '{node.name if node else node_id}': {message}")
    redraw_all()


def _hook(exc_type, exc, tb):
    try:
        _blame(exc_type, exc, tb)
    except Exception:
        pass
    (_original or sys.__excepthook__)(exc_type, exc, tb)


def register():
    global _original
    if sys.excepthook is not _hook:
        _original = sys.excepthook
        sys.excepthook = _hook


def unregister():
    global _original
    if sys.excepthook is _hook:
        sys.excepthook = _original or sys.__excepthook__
    _original = None
