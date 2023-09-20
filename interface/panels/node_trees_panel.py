import bpy

from ...utils.is_serpens import in_sn_tree
from ..ui_lists.nodetree_list import SN_UL_NodeTreesList


class SN_PT_NodeTreesPanel(bpy.types.Panel):
    bl_idname = "SN_PT_NodeTreesPanel"
    bl_label = "Node Trees"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Serpens"
    bl_order = 1

    @classmethod
    def poll(cls, context: bpy.types.Context): return in_sn_tree(context)

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        sn = context.scene.sn

        row = layout.row(align=True)
        row.template_list(SN_UL_NodeTreesList.bl_idname, "sn_node_trees", bpy.data, "node_groups", sn, "active_nodetree_index")

        col = row.column(align=True)
        col.operator("sn.add_nodetree", icon="ADD", text="")
