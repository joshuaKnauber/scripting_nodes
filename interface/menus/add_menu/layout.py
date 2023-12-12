import bpy

from ....core.nodes.Layout.PortalIn import SNA_NodePortalIn
from ....core.nodes.Layout.PortalOut import SNA_NodePortalOut


class SNA_MT_LayoutMenu(bpy.types.Menu):
    bl_idname = "SNA_MT_LayoutMenu"
    bl_label = "Layout"

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        op = layout.operator("node.add_node", text="Portal In")
        op.type = SNA_NodePortalIn.bl_idname
        op.use_transform = True

        op = layout.operator("node.add_node", text="Portal Out")
        op.type = SNA_NodePortalOut.bl_idname
        op.use_transform = True

        op = layout.operator("node.add_node", text="Frame")
        op.type = "NodeFrame"
        op.use_transform = True

        op = layout.operator("node.add_node", text="Reroute")
        op.type = "NodeReroute"
        op.use_transform = True
