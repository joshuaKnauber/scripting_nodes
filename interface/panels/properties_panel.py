import bpy
from ...utils.is_serpens import in_sn_tree


class SN_PT_PropertyPanel(bpy.types.Panel):
    bl_idname = "SN_PT_PropertyPanel"
    bl_label = "Properties"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 3

    @classmethod
    def poll(cls, context: bpy.types.Context): return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sn = context.scene.sn
