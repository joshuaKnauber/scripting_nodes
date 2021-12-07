import bpy



class SN_PT_AddonInfoPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonInfoPanel"
    bl_label = "Addon"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 4

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree

    def draw(self, context):
        layout = self.layout
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
        # row = col.row()
        # row.scale_y = 0.7
        # row.operator("sn.export_to_marketplace",text="Add to Marketplace",icon_value=bpy.context.scene.sn_icons[ "discord" ].icon_id)