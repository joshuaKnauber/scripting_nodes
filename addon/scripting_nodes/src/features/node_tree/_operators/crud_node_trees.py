from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import (
    scripting_node_trees,
)
from scripting_nodes.src.features.node_tree.node_tree import ScriptingNodeTree
import bpy


class SNA_OT_AddNodeTree(bpy.types.Operator):
    bl_idname = "sna.add_node_tree"
    bl_label = "Add Node Tree"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context: bpy.types.Context):
        ntree = bpy.data.node_groups.new("Node Tree", ScriptingNodeTree.bl_idname)
        context.space_data.node_tree = ntree
        for i, node_tree in enumerate(bpy.data.node_groups):
            if node_tree == ntree:
                context.scene.sna.ui.active_ntree_index = i
                break
        context.scene.sna.addon.is_dirty = True
        return {"FINISHED"}


class SNA_OT_RemoveNodeTree(bpy.types.Operator):
    bl_idname = "sna.remove_node_tree"
    bl_label = "Remove Node Tree"
    bl_options = {"REGISTER", "INTERNAL"}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        groups = scripting_node_trees()
        return len(groups) > 0 and context.scene.sna.ui.active_ntree_index < len(groups)

    def execute(self, context: bpy.types.Context):
        ntree = bpy.data.node_groups[context.scene.sna.ui.active_ntree_index]
        bpy.data.node_groups.remove(ntree)
        context.scene.sna.ui.active_ntree_index = min(0, len(bpy.data.node_groups) - 1)
        context.scene.sna.addon.is_dirty = True
        return {"FINISHED"}
