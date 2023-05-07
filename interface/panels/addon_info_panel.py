import bpy


class SN_PT_AddonInfoPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonInfoPanel"
    bl_label = "Addon Info"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return (
            context.space_data.tree_type == "ScriptingNodesTree"
            and context.space_data.node_tree
        )

    def draw_header(self, context):
        layout = self.layout
        sn = context.scene.sn
        layout.prop(sn, "use_addon", text="")
        layout.separator(factor=0.25)

    def draw(self, context):
        layout = self.layout
        layout.enabled = context.scene.sn.use_addon
        sn = context.scene.sn

        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(sn.info, "addon_name")
        layout.prop(sn.info, "description")
        layout.prop(sn.info, "author")
        layout.prop(sn.info, "location")
        layout.prop(sn.info, "warning")
        layout.prop(sn.info, "doc_url")
        layout.prop(sn.info, "tracker_url")
        col = layout.column(align=True)
        col.prop(sn.info, "category")
        if sn.info.category == "CUSTOM":
            col.prop(sn.info, "custom_category", text=" ")
        layout.prop(sn.info, "version")
        layout.prop(sn.info, "blender")

        # row = layout.row()
        # row.scale_y = 1.5
        # col = row.column(align=True)
        # col.operator("sn.export_addon", text="Save Addon", icon="EXPORT")

        # col.separator()
        # row = layout.row()
        # row.alert = True
        # row.label(text="Restart to see changes", icon="INFO")


class SN_PT_AddonDetailsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonDetailsPanel"
    bl_parent_id = "SN_PT_AddonInfoPanel"
    bl_label = "Addon Details"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return (
            context.space_data.tree_type == "ScriptingNodesTree"
            and context.space_data.node_tree
        )

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn
        layout.enabled = context.scene.sn.use_addon

        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(sn.info, "short_identifier")
