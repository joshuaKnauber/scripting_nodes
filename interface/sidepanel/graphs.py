import bpy


class SN_PT_GraphPanel(bpy.types.Panel):
    bl_idname = "SN_PT_GraphPanel"
    bl_label = "Addon Graphs"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 0

    def draw(self, context):
        layout = self.layout

        layout.label(text="Hello World")

        addon_tree = bpy.data.node_groups[context.scene.sn.editing_addon]

        layout.template_list("SN_UL_GraphList", "The_List", addon_tree, "sn_graphs", addon_tree, "sn_graph_index")
        layout.operator("sn.add_graph")