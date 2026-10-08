"""Node groups as Python functions.

A tree with a group interface (sidebar "Group" tab, Group Input / Group
Output nodes) is a function. Its interface decides how it is called:

  - a Program/Logic flow input: a statement, the body starts at Group
    Input's flow; a flow output is where the caller continues
  - an Interface flow input: a statement that draws UI into `layout`
  - no flow sockets: an expression (pure function)

Data inputs are the parameters, data outputs the return values. Both are
matched by the interface item's identifier, so renaming or reordering never
breaks links.

    def <tree.module_name>(param, ..., *, self=None, context=None, layout=None, event=None):
"""

import keyword

from ..sockets.socket_types import FLOW_SOCKET
from . import naming

GROUP_INPUT = "NodeGroupInput"
GROUP_OUTPUT = "NodeGroupOutput"
# keyword-only parameters every function takes from its caller
IMPLICIT = ("self", "context", "layout", "event")


def sockets(tree, in_out):
    return [
        item
        for item in tree.interface.items_tree
        if item.item_type == "SOCKET" and item.in_out == in_out
    ]


def is_flow(item):
    return item.bl_socket_idname == FLOW_SOCKET


def is_function(tree) -> bool:
    if any(item.item_type == "SOCKET" for item in tree.interface.items_tree):
        return True
    return any(node.bl_idname in (GROUP_INPUT, GROUP_OUTPUT) for node in tree.nodes)


def flow_input(tree):
    return next((item for item in sockets(tree, "INPUT") if is_flow(item)), None)


def flow_output(tree):
    return next((item for item in sockets(tree, "OUTPUT") if is_flow(item)), None)


def returns(tree):
    """Data output items, in order."""
    return [item for item in sockets(tree, "OUTPUT") if not is_flow(item)]


def parameters(tree):
    """[(item, Python name)] of the data inputs, in order."""
    used = set(IMPLICIT)
    result = []
    for item in sockets(tree, "INPUT"):
        if is_flow(item):
            continue
        base = naming.identifier(item.name.lower(), "value")
        if keyword.iskeyword(base):
            base += "_"
        name, i = base, 2
        while name in used:
            name, i = f"{base}_{i}", i + 1
        used.add(name)
        result.append((item, name))
    return result


def problem(tree) -> str | None:
    """Why the interface can't be compiled, or None."""
    flows_in = [item for item in sockets(tree, "INPUT") if is_flow(item)]
    flows_out = [item for item in sockets(tree, "OUTPUT") if is_flow(item)]
    if len(flows_in) > 1:
        return f"'{tree.name}' has more than one flow input"
    if len(flows_out) > 1:
        return f"'{tree.name}' has more than one flow output"
    if flows_out and not flows_in:
        return f"'{tree.name}' has a flow output but no flow input"
    return None


def active_output(tree):
    """The Group Output node that returns the values."""
    outputs = [node for node in tree.nodes if node.bl_idname == GROUP_OUTPUT]
    return next((node for node in outputs if node.is_active_output), None) or (
        outputs[0] if outputs else None
    )


def group_inputs(tree):
    return [node for node in tree.nodes if node.bl_idname == GROUP_INPUT]


def calls(tree, target, seen=None) -> bool:
    """Whether `tree` calls `target`, directly or through other functions."""
    seen = set() if seen is None else seen
    for node in tree.nodes:
        called = getattr(node, "node_tree", None)
        if node.bl_idname != "SNA_Node_Group" or called is None:
            continue
        if called == target:
            return True
        if called.name not in seen:
            seen.add(called.name)
            if calls(called, target, seen):
                return True
    return False


def sync_io_sockets(tree):
    """Blender sets up Group Input / Output sockets from their interface
    item only once; keep their settings (flow kind, vector size) and shape
    current.
    Returns True if anything changed."""
    changed = False
    items = {item.identifier: item for item in tree.interface.items_tree}
    for node in tree.nodes:
        if node.bl_idname not in (GROUP_INPUT, GROUP_OUTPUT):
            continue
        for socket in list(node.inputs) + list(node.outputs):
            item = items.get(socket.identifier)
            shape = getattr(socket, "socket_shape", None)
            if shape and socket.display_shape != shape:
                socket.display_shape = shape  # Blender resets it
                changed = True
            for name in getattr(item, "settings", ()):
                value = getattr(item, name)
                if getattr(socket, name) != value:
                    setattr(socket, name, value)
                    changed = True
    return changed


def callers(tree):
    """Group nodes calling `tree`, in all trees."""
    from ..lib.trees import scripting_node_trees, sn_nodes

    return [
        node
        for other in scripting_node_trees()
        for node in sn_nodes(other)
        if node.bl_idname == "SNA_Node_Group" and node.node_tree == tree
    ]
