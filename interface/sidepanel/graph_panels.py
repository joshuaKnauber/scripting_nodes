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
        col = row.column(align=True)
        col.template_list("SN_UL_VariableList", "Variables", graph_tree, "sn_variables", graph_tree, "sn_variable_index")
        if len(graph_tree.sn_variables):
            btn_row = col.row(align=True)
            btn_row.operator("sn.add_getter",icon="SORT_DESC")
            btn_row.operator("sn.add_setter",icon="SORT_ASC")
        col = row.column(align=True)
        col.operator("sn.add_variable", text="", icon="ADD")
        col.operator("sn.remove_variable", text="", icon="REMOVE")
        
        if len(graph_tree.sn_variables):
            layout.separator()
            row = layout.row()
            col = row.column()
            col.use_property_split = True
            col.use_property_decorate = False
            var = graph_tree.sn_variables[graph_tree.sn_variable_index]
            
            col.prop(var,"var_type",text="Type")
            col.prop(var,"name",text="Name")
            
            row.label(text="",icon="BLANK1")