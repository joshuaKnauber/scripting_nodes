import bpy
from ..core.node_tree.node_tree import ScriptingNodesTree


def in_sn_tree(context: bpy.types.Context) -> bool:
    return (
        context.space_data.node_tree != None
        and context.space_data.node_tree.bl_idname == ScriptingNodesTree.bl_idname
    )
