import bpy


def get_node_tree_by_id(id: str):
    """Returns the node tree with the given id"""
    for ntree in bpy.data.node_groups:
        if getattr(ntree, "id", "") == id:
            return ntree
    return None
