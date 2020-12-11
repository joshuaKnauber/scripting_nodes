import bpy


class SN_PT_GraphPanel(bpy.types.Panel):
    bl_idname = "SN_PT_GraphPanel"
    bl_label = "Graphs"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return context.scene.sn.editing_addon != "NONE" and context.space_data.tree_type == "ScriptingNodesTree"

    def draw(self, context):
        layout = self.layout

        addon_tree = context.scene.sn.addon_tree()

        list_col = layout.column(align=True)
        row = list_col.row(align=True)
        row.template_list("SN_UL_GraphList", "The_List", addon_tree, "sn_graphs", addon_tree, "sn_graph_index")
        col = row.column(align=True)
        col.operator("sn.add_graph", text="", icon="ADD")
        col.operator("sn.remove_graph", text="", icon="REMOVE").index = addon_tree.sn_graph_index

        graph = addon_tree.sn_graphs[addon_tree.sn_graph_index]
        if addon_tree.sn_graph_index > 0:
            row = list_col.row(align=True)
            row.prop(graph, "name", text="")
            row.prop(graph, "bookmarked", text="", emboss=False, icon="BOOKMARKS" if graph.bookmarked else "BLANK1")


bpy.utils.register_class(SN_PT_GraphPanel)


class SN_PT_AddonInfoPanel(bpy.types.Panel):
    bl_parent_id = "SN_PT_GraphPanel"
    bl_idname = "SN_PT_AddonInfoPanel"
    bl_label = "Addon Info"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"

    def draw(self, context):
        layout = self.layout

        addon_tree = context.scene.sn.addon_tree()
        graph = addon_tree.sn_graphs[addon_tree.sn_graph_index]
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(graph, "name", text="Name")
        layout.prop(graph, "description", text="Description")
        layout.prop(graph, "author", text="Author")
        layout.prop(graph, "location", text="Location")
        layout.prop(graph, "warning", text="Warning")
        layout.prop(graph, "wiki_url", text="Wiki URL")
        layout.prop(graph, "tracker_url", text="Tracker URL")
        col = layout.column(align=True)
        col.prop(graph, "category", text="Category")
        if graph.category == "CUSTOM":
            col.prop(graph, "custom_category", text=" ")
        layout.prop(graph, "version", text="Version")
        layout.prop(graph, "blender", text="Blender")