import bpy

from ...utils.is_serpens import in_sn_tree


class SN_PT_AddonPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonPanel"
    bl_label = "Addon"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_order = 0
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: bpy.types.Context): return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sn = context.scene.sn

        layout.use_property_split = True
        layout.use_property_decorate = False

        if sn.info.has_changes:
            box = layout.box()
            box.alert = True
            col = box.column(align=True)
            col.label(text="Addon Info Changes", icon="INFO")
            row = col.row()
            row.enabled = False
            row.label(text="Restart required to update preferences.")
            layout.separator()

        col = layout.column(heading="Info")

        col.prop(sn.info, "name")
        col.prop(sn.info, "description")
        col.prop(sn.info, "author")

        layout.separator()
        layout.prop(sn.info, "persist_sessions")
        layout.separator()

        row = layout.row()
        row.scale_y = 1.5
        row.operator("sn.export_addon", icon="EXPORT", text=f"Export Addon {'.'.join(map(str, list(sn.info.version)))}")


class SN_PT_AddonInfoPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonInfoPanel"
    bl_parent_id = SN_PT_AddonPanel.bl_idname
    bl_label = "Addon Info"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 0

    @classmethod
    def poll(cls, context: bpy.types.Context): return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sn = context.scene.sn

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.prop(sn.info, "version")
        col.prop(sn.info, "blender")
        col.prop(sn.info, "location")
        col.prop(sn.info, "warning")
        col.prop(sn.info, "doc_url")
        col.prop(sn.info, "tracker_url")
        col.prop(sn.info, "category")
        if sn.info.category == "CUSTOM":
            col.prop(sn.info, "custom_category")


class SN_PT_AddonDetailsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonDetailsPanel"
    bl_parent_id = SN_PT_AddonPanel.bl_idname
    bl_label = "Addon Details"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 1

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
