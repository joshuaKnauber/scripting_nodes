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
        return context.scene.sn.editing_addon != "NONE"

    def draw(self, context):
        layout = self.layout

        addon_tree = context.scene.sn.addon_tree()

        row = layout.row(align=True)
        row.template_list("SN_UL_GraphList", "The_List", addon_tree, "sn_graphs", addon_tree, "sn_graph_index")
        col = row.column(align=True)
        col.operator("sn.add_graph", text="", icon="ADD")
        col.operator("sn.remove_graph", text="", icon="REMOVE").index = addon_tree.sn_graph_index

        row = layout.row(align=True)
        if len(addon_tree.sn_graphs):
            graph = addon_tree.sn_graphs[addon_tree.sn_graph_index]
            row.prop(graph, "name", text="")