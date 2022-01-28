import bpy



class SN_PT_VariablePanel(bpy.types.Panel):
    bl_parent_id = "SN_PT_GraphPanel"
    bl_idname = "SN_PT_VariablePanel"
    bl_label = "Variables"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn
        if len(bpy.data.node_groups) > sn.node_tree_index:
            ntree = bpy.data.node_groups[sn.node_tree_index]
            
            # draw variable ui list
            row = layout.row(align=False)
            col = row.column(align=True)
            col.template_list("SN_UL_VariableList", "Variables", ntree, "variables", ntree, "variable_index", rows=4)
            col.operator("sn.add_variable_node", text="Add Node", icon="ADD").node_tree = ntree.name
            col = row.column(align=True)
            col.operator("sn.add_variable", text="", icon="ADD").node_tree = ntree.name
            col.operator("sn.add_variable", text="", icon="VIEWZOOM").node_tree = ntree.name
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