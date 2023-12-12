import bpy

from ..nodes.utils.references import collection


def get_node_by_id(id: str):
    """Returns the node with the given id"""
    for ntree in bpy.data.node_groups:
        if getattr(ntree, "is_sn_ntree", False):
            for node in ntree.nodes:
                if node.get("id", None) == id:
                    return node
    return None


def get_ref_by_id(id: str):
    """Returns the node ref with the given id"""
    node = get_node_by_id(id)
    coll = collection(node.bl_idname)
    if coll:
        return coll.get_ref_by_id(id)
    return None
