from .is_sn import is_sn
import bpy


def scripting_node_trees():
    return [ntree for ntree in bpy.data.node_groups if is_sn(ntree)]


def has_addon():
    return len(scripting_node_trees()) > 0


def sn_nodes(ntree):
    return [node for node in ntree.nodes if is_sn(node)]


# {node id: (tree name, node name)}. Names instead of node objects: Python
# references to nodes become invalid after undo. A hit is verified by name,
# a miss rebuilds the index once; ids that are still missing after that are
# remembered until `forget_missing()` (called on every rebuild of the addon).
_index: dict[str, tuple[str, str]] = {}
_missing: set[str] = set()


def _cached(node_id):
    names = _index.get(node_id)
    if names is None:
        return None
    tree = bpy.data.node_groups.get(names[0])
    node = tree.nodes.get(names[1]) if tree is not None else None
    if node is not None and getattr(node, "id", None) == node_id:
        return node
    return None


def _rebuild_index():
    _index.clear()
    for ntree in scripting_node_trees():
        for node in sn_nodes(ntree):
            if node.id:
                _index[node.id] = (ntree.name, node.name)


def node_by_id(node_id):
    if not node_id or node_id in _missing:
        return None
    node = _cached(node_id)
    if node is None:
        _rebuild_index()
        node = _cached(node_id)
        if node is None:
            _missing.add(node_id)
    return node


def forget_missing():
    """Look up missing ids again (nodes may have been added or restored)."""
    _missing.clear()
