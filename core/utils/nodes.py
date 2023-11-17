import bpy


def get_node_by_id(id: str):
    """ Returns the node with the given id """
    for ntree in bpy.data.node_groups:
        if getattr(ntree, "is_sn", False):
            for node in ntree.nodes:
                if node.get("id", None) == id:
                    return node
    return None
