import bpy

from ..utils.references import NodePointer, node_search

from ....constants import sockets
from ..base_node import SNA_BaseNode


class SNA_NodePortalOut(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodePortalOut"
    bl_label = "Portal Out"
    bl_width_default = 100

    portal: bpy.props.PointerProperty(type=NodePointer)

    def on_reference_update(self, node):
        self.color = node.color
        self.mark_dirty()

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        node_search(layout, self.portal, "SNA_NodePortalIn")

    def draw_label(self):
        if self.portal.node:
            return self.portal.node.name
        return "Portal Out"

    def on_create(self):
        self.add_output(sockets.DATA)
        self.use_custom_color = True

    def generate(self, context, trigger):
        if self.portal.node:
            self.outputs[0].code = self.portal.node.inputs[0].get_code()
