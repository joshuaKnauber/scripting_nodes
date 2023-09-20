import bpy

from .node_tree import ScriptingNodesTree


class SN_OT_AddNodeTree(bpy.types.Operator):
    bl_idname = "sn.add_nodetree"
    bl_label = "Add Node Tree"
    bl_description = "Add a new node tree"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context):
        bpy.data.node_groups.new("NodeTree", ScriptingNodesTree.bl_idname)
        return {"FINISHED"}
