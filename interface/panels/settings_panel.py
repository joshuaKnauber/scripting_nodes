import bpy
from ...utils.is_serpens import in_sn_tree


class SN_PT_SettingsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_SettingsPanel"
    bl_label = "Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 4

    @classmethod
    def poll(cls, context: bpy.types.Context): return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sn = context.scene.sn

        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()
        col = layout.column(heading="Debug")
