"""Upgrade node trees saved by older versions of Scripting Nodes.

Every tree stores the data version it was last saved with
(`ScriptingNodeTree.data_version`). On load, each step from that version up to
`DATA_VERSION` runs in order. Add a new step whenever saved data changes shape
(renamed properties, bl_idnames, socket identifiers, enum items, ...).
"""

from ..lib.logger import log

DATA_VERSION = 3


def _script_functions(tree):
    """Script nodes pick the function they call (they always called run())."""
    for node in tree.nodes:
        if node.bl_idname != "SNA_Node_Script" or node.function_name:
            continue
        if "run" in node.script_functions():
            node.function_name = "run"


def _renamed_nodes(tree):
    """Nodes whose bl_idname changed (nodes/_renamed.py) become the renamed
    node: same settings, input values, links and id."""
    for node in list(tree.nodes):
        new_idname = getattr(node, "sn_renamed_to", None)
        if new_idname:
            replace_node(tree, node, new_idname)


def replace_node(tree, node, idname):
    new = tree.nodes.new(idname)
    for attr in ("location", "width", "label", "hide", "mute", "parent"):
        setattr(new, attr, getattr(node, attr))
    # settings the node classes define (incl. its id: references keep working)
    for prop in node.bl_rna.properties:
        name = prop.identifier
        if not prop.is_runtime or prop.is_readonly or prop.type == "COLLECTION":
            continue
        if name in new.bl_rna.properties:
            setattr(new, name, getattr(node, name))
    new.sync_sockets()
    for old_sockets, new_sockets in (
        (node.inputs, new.inputs),
        (node.outputs, new.outputs),
    ):
        for socket in old_sockets:
            target = next(
                (s for s in new_sockets if s.identifier == socket.identifier), None
            )
            if target is None:
                continue
            if hasattr(socket, "value") and hasattr(target, "value"):
                target.value = socket.value
            for link in socket.links:
                if socket.is_output:
                    tree.links.new(target, link.to_socket)
                else:
                    tree.links.new(link.from_socket, target)
    name = node.name
    tree.nodes.remove(node)
    new.name = name
    return new


# data version -> function(tree) bringing a tree from version - 1 to it
STEPS = {2: _script_functions, 3: _renamed_nodes}


def upgrade(trees):
    for tree in trees:
        version = tree.data_version
        if version >= DATA_VERSION:
            continue
        for step in range(version + 1, DATA_VERSION + 1):
            try:
                STEPS[step](tree)
            except Exception as exc:
                log("ERROR", f"Upgrading '{tree.name}' to data version {step}: {exc}")
        tree.data_version = DATA_VERSION
