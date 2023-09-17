import bpy

from ...utils.is_serpens import in_sn_tree


class SN_PT_AddonPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonPanel"
    bl_label = "Addon"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Serpens"
    bl_order = 0

    @classmethod
    def poll(cls, context: bpy.types.Context): return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sn = context.scene.sn

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(heading="Info")

        col.prop(sn.info, "name")
        col.prop(sn.info, "description")

        layout.separator()

        row = layout.row()
        row.scale_y = 1.5
        row.operator("sn.export_addon", icon="EXPORT")
        layout.prop(sn.info, "persist_sessions")


class SN_PT_AddonDetailsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonDetailsPanel"
    bl_parent_id = SN_PT_AddonPanel.bl_idname
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

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()

        row = col.row(heading="Module Name")
        row.prop(sn.info, "use_custom_module_name", text="")
        subrow = row.row()
        subrow.enabled = sn.info.use_custom_module_name
        subrow.prop(sn.info, "module_name", text="")

        row = col.row(heading="Shorthand")
        row.prop(sn.info, "use_custom_shorthand", text="")
        subrow = row.row()
        subrow.enabled = sn.info.use_custom_shorthand
        subrow.prop(sn.info, "shorthand", text="")
