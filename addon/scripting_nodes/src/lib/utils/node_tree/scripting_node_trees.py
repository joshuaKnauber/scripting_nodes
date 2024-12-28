from ..is_sn import is_sn
import bpy


def scripting_node_trees():
    return [ntree for ntree in bpy.data.node_groups if is_sn(ntree)]


def has_addon():
    return len(scripting_node_trees()) > 0


def sn_nodes(ntree):
    return [node for node in ntree.nodes if is_sn(node)]


def node_by_id(node_id):
    for ntree in scripting_node_trees():
        for node in sn_nodes(ntree):
            if node.id == node_id:
                return node
    return None
