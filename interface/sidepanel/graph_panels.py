import bpy


class SN_OT_GetPythonName(bpy.types.Operator):
    bl_idname = "sn.get_python_name"
    bl_label = "Get Python Name"
    bl_description = "Get the python name for this element"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    to_copy: bpy.props.StringProperty()

    def execute(self, context):
        bpy.context.window_manager.clipboard = self.to_copy
        self.report({"INFO"},message="Python path copied")
        return {"FINISHED"}


class SN_PT_GraphPanel(bpy.types.Panel):
    bl_idname = "SN_PT_GraphPanel"
    bl_label = "Graphs"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn

        row = layout.row(align=False)
        row.template_list("SN_UL_GraphList", "Graphs", bpy.data, "node_groups", sn, "node_tree_index", rows=4)
        col = row.column(align=True)
        col.operator("node.new_node_tree", text="", icon="ADD")
        col.operator("sn.append_graph", text="", icon="APPEND_BLEND")
        col.operator("sn.remove_graph", text="", icon="TRASH").index = sn.node_tree_index


        # col.separator()
        # row = col.row(align=True)
        # row.enabled = addon_tree.sn_graph_index > 1
        # row.operator("sn.move_graph", text="", icon="TRIA_UP").up = True
        # row = col.row(align=True)
        # row.enabled = addon_tree.sn_graph_index < len(addon_tree.sn_graphs)-1
        # row.operator("sn.move_graph", text="", icon="TRIA_DOWN").up = False