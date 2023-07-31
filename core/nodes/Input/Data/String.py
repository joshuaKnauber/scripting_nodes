import bpy

from .....constants import sockets
from ...base_node import SN_BaseNode


class SN_StringNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_StringNode"
    bl_label = "String"

    def on_create(self):
        out = self.add_output(sockets.STRING)
        out.draw_output_value = True
        out.draw_linked_value = True
