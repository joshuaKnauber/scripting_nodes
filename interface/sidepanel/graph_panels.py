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

        row = layout.row(align=False)
        row.template_list("SN_UL_GraphList", "Graphs", addon_tree, "sn_graphs", addon_tree, "sn_graph_index")
        col = row.column(align=True)
        col.operator("sn.add_graph", text="", icon="ADD")
        col.operator("sn.remove_graph", text="", icon="REMOVE").index = addon_tree.sn_graph_index


bpy.utils.register_class(SN_PT_GraphPanel)


class SN_PT_VariablePanel(bpy.types.Panel):
    bl_parent_id = "SN_PT_GraphPanel"
    bl_idname = "SN_PT_VariablePanel"
    bl_label = "Variables"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 1

    def draw(self, context):
        layout = self.layout

        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree

        row = layout.row(align=False)
        row.template_list("SN_UL_VariableList", "Variables", graph_tree, "sn_variables", graph_tree, "sn_variable_index")
        col = row.column(align=True)
        col.operator("sn.add_variable", text="", icon="ADD")
        col.operator("sn.remove_variable", text="", icon="REMOVE")



class SN_PT_AddonInfoPanel(bpy.types.Panel):
    bl_parent_id = "SN_PT_GraphPanel"
    bl_idname = "SN_PT_AddonInfoPanel"
    bl_label = "Addon Info"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 2

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