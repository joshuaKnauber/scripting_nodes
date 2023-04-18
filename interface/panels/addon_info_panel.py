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
        layout.prop(sn, "addon_name")
        layout.prop(sn, "description")
        layout.prop(sn, "author")
        layout.prop(sn, "location")
        layout.prop(sn, "warning")
        layout.prop(sn, "doc_url")
        layout.prop(sn, "tracker_url")
        col = layout.column(align=True)
        col.prop(sn, "category")
        if sn.category == "CUSTOM":
            col.prop(sn, "custom_category", text=" ")
        layout.prop(sn, "version")
        layout.prop(sn, "blender")

        row = layout.row()
        row.scale_y = 1.5
        col = row.column(align=True)
        col.operator("sn.export_addon", text="Save Addon", icon="EXPORT")
