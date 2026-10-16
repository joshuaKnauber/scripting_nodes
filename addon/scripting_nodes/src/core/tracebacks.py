"""Show exceptions raised by the running generated addon on their node.

After the runtime imports the generated addon (before its register()), the
functions of its modules and the methods Blender calls on its classes
(execute, draw, ...) are wrapped: an exception is mapped back to the node
that wrote the failing line (via the compiler's line map), shown on that node
and raised again, so Blender reports it as usual. The generated code contains
nothing for this, and `sys` is left alone (extensions mustn't change it).

Not covered: functions bound before the wrapping, e.g. a property's
`update=` callback or a function another module imported.
"""

import functools
import inspect
import os
import sys
import traceback
import types

from ..lib.logger import log
from . import errors

# methods Blender calls on registered classes
METHODS = (
    "execute",
    "invoke",
    "modal",
    "cancel",
    "check",
    "draw",
    "draw_header",
    "draw_header_preset",
    "draw_item",
    "filter_items",
)


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
    from ..lib.screen import redraw_all
    from ..lib.trees import node_by_id

    node = node_by_id(node_id)
    log("ERROR", f"Error in node '{node.name if node else node_id}': {message}")
    redraw_all()


def _report(exc):
    try:
        _blame(type(exc), exc, exc.__traceback__)
    except Exception:  # noqa: BLE001 - never hide the add-on's own error
        traceback.print_exc()


def _wrap(fn):
    """`fn` reporting its exceptions. Wrappers of methods keep their exact
    parameters: Blender checks them when classes are registered."""
    params = list(inspect.signature(fn).parameters.values())
    plain = all(
        p.kind is p.POSITIONAL_OR_KEYWORD and p.default is p.empty for p in params
    )
    if plain:
        names = ", ".join(p.name for p in params)
        namespace = {"_fn": fn, "_report": _report}
        # a wrapper with the same parameters
        exec(
            f"def wrapper({names}):\n"
            f"    try:\n"
            f"        return _fn({names})\n"
            f"    except Exception as exc:\n"
            f"        _report(exc)\n"
            f"        raise\n",
            namespace,
        )
        wrapper = functools.wraps(fn)(namespace["wrapper"])
    else:

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                _report(exc)
                raise

    wrapper._sn_wrapped = True
    return wrapper


def instrument(package):
    """Wrap the functions and methods of the generated addon `package` (its
    modules are imported, register() hasn't run)."""
    for name, module in list(sys.modules.items()):
        if module is None or not (name == package or name.startswith(package + ".")):
            continue
        for attr, value in list(vars(module).items()):
            if getattr(value, "__module__", None) != name:
                continue
            if isinstance(value, types.FunctionType):
                if not getattr(value, "_sn_wrapped", False):
                    setattr(module, attr, _wrap(value))
            elif isinstance(value, type):
                for method in METHODS:
                    fn = value.__dict__.get(method)
                    if isinstance(fn, types.FunctionType) and not getattr(
                        fn, "_sn_wrapped", False
                    ):
                        setattr(value, method, _wrap(fn))
