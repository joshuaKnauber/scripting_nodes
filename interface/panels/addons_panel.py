import bpy

from ...utils.is_serpens import in_sn_tree


class SNA_PT_AddonPanel(bpy.types.Panel):
    bl_idname = "SNA_PT_AddonPanel"
    bl_label = "Addon"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_order = 0
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sna = context.scene.sna

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(heading="Info")

        col.prop(sna.info, "name")
        col.prop(sna.info, "description")
        col.prop(sna.info, "author")

        layout.separator()
        layout.prop(sna.info, "persist_sessions")
        layout.separator()

        if sna.info.has_changes:
            box = layout.box()
            box.alert = True
            col = box.column(align=True)
            col.label(text="Addon Info Changes", icon="INFO")
            row = col.row()
            row.enabled = False
            row.label(text="Restart required to update preferences.")
            layout.separator()

        row = layout.row()
        row.scale_y = 1.5
        row.operator(
            "sna.export_addon",
            icon="EXPORT",
            text=f"Export Addon {'.'.join(map(str, list(sna.info.version)))}",
        )


class SNA_PT_AddonInfoPanel(bpy.types.Panel):
    bl_idname = "SNA_PT_AddonInfoPanel"
    bl_parent_id = SNA_PT_AddonPanel.bl_idname
    bl_label = "Addon Info"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 0

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sna = context.scene.sna

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.prop(sna.info, "version")
        col.prop(sna.info, "blender")
        col.prop(sna.info, "location")
        col.prop(sna.info, "warning")
        col.prop(sna.info, "doc_url")
        col.prop(sna.info, "tracker_url")
        col.prop(sna.info, "category")
        if sna.info.category == "CUSTOM":
            col.prop(sna.info, "custom_category")


class SNA_PT_AddonDetailsPanel(bpy.types.Panel):
    bl_idname = "SNA_PT_AddonDetailsPanel"
    bl_parent_id = SNA_PT_AddonPanel.bl_idname
    bl_label = "Addon Details"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 1

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sna = context.scene.sna

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()

        row = col.row(heading="Module Name")
        row.prop(sna.info, "use_custom_module_name", text="")
        subrow = row.row()
        subrow.enabled = sna.info.use_custom_module_name
        subrow.prop(sna.info, "custom_module_name", text="")

        row = col.row(heading="Shorthand")
        row.prop(sna.info, "use_custom_shorthand", text="")
        subrow = row.row()
        subrow.enabled = sna.info.use_custom_shorthand
        subrow.prop(sna.info, "shorthand", text="")
