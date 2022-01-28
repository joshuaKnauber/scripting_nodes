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
            col.operator("sn.add_property_node", text="Add Node", icon="ADD")
            col = row.column(align=True)
            col.operator("sn.add_property", text="", icon="ADD")
            col.operator("sn.add_property", text="", icon="VIEWZOOM")
            col.operator("sn.remove_property", text="", icon="REMOVE")

            col.separator()
            subrow = col.row(align=True)
            subrow.enabled = ntree.variable_index > 0
            op = subrow.operator("sn.move_property", text="", icon="TRIA_UP")
            op.move_up = True
            subrow = col.row(align=True)
            subrow.enabled = ntree.variable_index < len(ntree.variables)-1
            op = subrow.operator("sn.move_property", text="", icon="TRIA_DOWN")
            op.move_up = False
            layout.separator()