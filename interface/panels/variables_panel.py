import bpy

from ...utils.is_serpens import in_sn_tree


class SN_PT_VariablePanel(bpy.types.Panel):
    bl_idname = "SN_PT_VariablePanel"
    bl_label = "Variables"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 2

    @classmethod
    def poll(cls, context: bpy.types.Context): return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sn = context.scene.sn
        ntree = context.space_data.node_tree
