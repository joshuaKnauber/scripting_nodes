from scripting_nodes.src.features.node_tree.node_tree import ScriptingNodeTree
import bpy


def in_sn_tree(context):
    return (
        context.space_data.node_tree != None
        and context.space_data.node_tree.bl_idname == ScriptingNodeTree.bl_idname
    )


def is_sn_editor(context: bpy.types.Context):
    return context.area.ui_type == ScriptingNodeTree.bl_idname
