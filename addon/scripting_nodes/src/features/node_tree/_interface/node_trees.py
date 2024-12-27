import bpy


class SNA_PT_NodeTrees(bpy.types.Panel):
    bl_idname = "SNA_PT_NodeTrees"
    bl_label = "Node Trees"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_order = 1

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.template_list(
            "SNA_UL_NodeTreesList",
            "",
            bpy.data,
            "node_groups",
            context.scene.sna.ui,
            "active_ntree_index",
        )

        col = row.column(align=True)
        col.operator("sna.add_node_tree", icon="ADD", text="")
        col.operator("sna.remove_node_tree", icon="REMOVE", text="")
        col.separator()
        col.operator("wm.append", icon="APPEND_BLEND", text="")
