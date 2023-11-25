import bpy

from ...utils.is_serpens import in_sn_tree
from ..ui_lists.nodetree_list import SNA_UL_NodeTreesList


class SNA_PT_NodeTreesPanel(bpy.types.Panel):
    bl_idname = "SNA_PT_NodeTreesPanel"
    bl_label = "Node Trees"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_order = 1

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sna = context.scene.sna

        row = layout.row()
        row.template_list(
            SNA_UL_NodeTreesList.bl_idname,
            "sn_node_trees",
            bpy.data,
            "node_groups",
            sna,
            "active_nodetree_index",
        )

        col = row.column(align=True)
        col.operator("sna.add_nodetree", icon="ADD", text="")
        col.operator("wm.append", icon="APPEND_BLEND", text="")
        subrow = col.row(align=True)
        subrow.enabled = sna.active_nodetree_index <= len(bpy.data.node_groups) - 1
        subrow.operator("sna.remove_nodetree", icon="REMOVE", text="")
