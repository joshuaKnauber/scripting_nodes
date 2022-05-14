import bpy



class SN_PT_VariablePanel(bpy.types.Panel):
    bl_parent_id = "SN_PT_GraphPanel"
    bl_idname = "SN_PT_VariablePanel"
    bl_label = ""
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED", "HEADER_LAYOUT_EXPAND"}
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Variables")
        layout.operator("wm.url_open", text="", icon="QUESTION", emboss=False).url = "https://joshuaknauber.notion.site/Variables-ff5e8ae2e4154c8fa9eed43ecaa0c165"

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn
        ntree = context.space_data.node_tree
        
        # draw variable ui list
        row = layout.row(align=False)
        col = row.column(align=True)
        
        if sn.overwrite_variable_graph:
            col.prop(sn, "variable_graph", text="")
            ntree = bpy.data.node_groups[sn.variable_graph]

        col.template_list("SN_UL_VariableList", "Variables", ntree, "variables", ntree, "variable_index", rows=4)

        op = col.operator("sn.add_variable_node_popup", text="Add Node", icon="ADD")
        op.node_tree = ntree.name

        col = row.column(align=True)
        col.operator("sn.add_variable", text="", icon="ADD").node_tree = ntree.name
        col.operator("sn.find_variable", text="", icon="VIEWZOOM").node_tree = ntree.name
        col.operator("sn.remove_variable", text="", icon="REMOVE").node_tree = ntree.name

        col.separator()
        subrow = col.row(align=True)
        subrow.enabled = ntree.variable_index > 0
        op = subrow.operator("sn.move_variable", text="", icon="TRIA_UP")
        op.move_up = True
        op.node_tree = ntree.name
        subrow = col.row(align=True)
        subrow.enabled = ntree.variable_index < len(ntree.variables)-1
        op = subrow.operator("sn.move_variable", text="", icon="TRIA_DOWN")
        op.move_up = False
        op.node_tree = ntree.name
        layout.separator()
        
        if ntree.variable_index < len(ntree.variables):
            var = ntree.variables[ntree.variable_index]
            col = layout.column()
            col.use_property_split = True
            col.use_property_decorate = False
            
            col.prop(var, "variable_type")
            
            if var.variable_type == "String":
                col.separator()
                col.prop(var, "string_default")
            elif var.variable_type == "Boolean":
                col.separator()
                col.prop(var, "boolean_default")
            elif var.variable_type == "Float":
                col.separator()
                col.prop(var, "float_default")
            elif var.variable_type == "Integer":
                col.separator()
                col.prop(var, "integer_default")