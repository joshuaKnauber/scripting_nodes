"""Python-side error state shown in the UI.

Kept out of bpy data on purpose: errors describe the *current* session (a node
whose generate() raised, a generated addon that failed to load) and must never
be restored by undo or saved into the .blend.
"""

import traceback
from contextlib import contextmanager

# node id -> short message
node_errors: dict[str, str] = {}

# node id -> message, for nodes whose generated line made the addon fail to load
load_errors: dict[str, str] = {}

# node id -> message, for exceptions raised while the generated addon ran
# (e.g. clicking a generated button), see core/tracebacks.py
runtime_errors: dict[str, str] = {}

# property id -> message, for property definitions that can't be generated
property_errors: dict[str, str] = {}

# Error of the last attempt to load the generated addon (None when it loaded)
addon_error: str | None = None


@contextmanager
def kept():
    """Keep the live add-on's node and property errors while another build
    (the export, its check) runs: yields a dict that gets that build's node
    errors."""
    saved = dict(node_errors), dict(property_errors)
    found = {}
    try:
        yield found
    finally:
        found.update(node_errors)
        node_errors.clear()
        node_errors.update(saved[0])
        property_errors.clear()
        property_errors.update(saved[1])


def set_node_error(node_id: str, exc: BaseException):
    node_errors[node_id] = f"{type(exc).__name__}: {exc}"


def clear_node_error(node_id: str):
    node_errors.pop(node_id, None)


def set_addon_error(message: str | None, nodes: dict[str, str] | None = None):
    """Set (or clear with None) the addon load error and the nodes it blames."""
    global addon_error
    addon_error = message
    load_errors.clear()
    if message and nodes:
        load_errors.update(nodes)


def node_message(node_id: str) -> str | None:
    return (
        node_errors.get(node_id)
        or load_errors.get(node_id)
        or runtime_errors.get(node_id)
    )


def nodes_with_errors(tree=None):
    """Nodes showing an error, in `tree` or in all trees."""
    from ..lib.trees import scripting_node_trees, sn_nodes

    trees = [tree] if tree is not None else scripting_node_trees()
    return [node for t in trees for node in sn_nodes(t) if node_message(node.id)]


def format_exception(exc: BaseException) -> str:
    return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))


def clear():
    global addon_error
    node_errors.clear()
    load_errors.clear()
    runtime_errors.clear()
    property_errors.clear()
    addon_error = None
