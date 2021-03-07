import bpy



class SN_PT_AddonInfoPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonInfoPanel"
    bl_label = "Addon"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 2

    @classmethod
    def poll(cls, context):
        return context.scene.sn.editing_addon != "NONE" and context.space_data.tree_type == "ScriptingNodesTree"

    def draw(self, context):
        layout = self.layout

        addon_tree = context.scene.sn.addon_tree()
        addon_graph = addon_tree.sn_graphs[0]
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(addon_graph, "name", text="Name")
        layout.prop(addon_graph, "description", text="Description")
        layout.prop(addon_graph, "author", text="Author")
        layout.prop(addon_graph, "location", text="Location")
        layout.prop(addon_graph, "warning", text="Warning")
        layout.prop(addon_graph, "wiki_url", text="Wiki URL")
        layout.prop(addon_graph, "tracker_url", text="Tracker URL")
        col = layout.column(align=True)
        col.prop(addon_graph, "category", text="Category")
        if addon_graph.category == "CUSTOM":
            col.prop(addon_graph, "custom_category", text=" ")
        layout.prop(addon_graph, "version", text="Version")
        layout.prop(addon_graph, "blender", text="Blender")
        
        row = layout.row()
        row.scale_y = 1.5
        col = row.column(align=True)
        col.operator("sn.save_addon",text="Save Addon",icon="FILE_TICK")
        row = col.row()
        row.scale_y = 0.7
        row.operator("sn.export_to_marketplace",text="Add to Marketplace",icon_value=bpy.context.scene.sn_icons[ "discord" ].icon_id)