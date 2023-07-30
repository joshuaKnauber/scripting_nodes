import bpy
from ...utils.is_serpens import in_sn_tree


class SN_PT_AddonInfoPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonInfoPanel"
    bl_label = "Addon Info"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 0

    @classmethod
    def poll(cls, context: bpy.types.Context): return in_sn_tree(context)

    def draw_header(self, context: bpy.types.Context):
        layout = self.layout

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sn = context.scene.sn


class SN_PT_AddonDetailsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonDetailsPanel"
    bl_parent_id = SN_PT_AddonInfoPanel.bl_idname
    bl_label = "Addon Details"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: bpy.types.Context): return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sn = context.scene.sn
