import bpy

from ...core import scheduler
from ...lib.is_sn import is_sn
from ..node_tree import ScriptingNodeTree


def _active_tree(context):
    """The SN tree selected in the tree list (index into bpy.data.node_groups)."""
    index = context.scene.sna.ui.active_ntree_index
    groups = bpy.data.node_groups
    if 0 <= index < len(groups) and is_sn(groups[index]):
        return groups[index]
    return None


class SNA_OT_AddNodeTree(bpy.types.Operator):
    bl_idname = "sna.add_node_tree"
    bl_label = "Add Node Tree"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context: bpy.types.Context):
        ntree = bpy.data.node_groups.new("Node Tree", ScriptingNodeTree.bl_idname)
        ntree.init()
        if context.space_data and context.space_data.type == "NODE_EDITOR":
            context.space_data.node_tree = ntree
        context.scene.sna.ui.active_ntree_index = bpy.data.node_groups.find(ntree.name)
        scheduler.request_full()
        return {"FINISHED"}


class SNA_OT_RemoveNodeTree(bpy.types.Operator):
    bl_idname = "sna.remove_node_tree"
    bl_label = "Remove Node Tree"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return _active_tree(context) is not None

    def execute(self, context: bpy.types.Context):
        bpy.data.node_groups.remove(_active_tree(context))
        # select the closest remaining SN tree
        index = context.scene.sna.ui.active_ntree_index
        candidates = [i for i, g in enumerate(bpy.data.node_groups) if is_sn(g)]
        if candidates:
            closest = min(candidates, key=lambda i: abs(i - index))
            context.scene.sna.ui.active_ntree_index = closest
        scheduler.request_full()
        return {"FINISHED"}
