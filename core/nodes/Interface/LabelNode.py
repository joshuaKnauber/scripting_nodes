import bpy

from ....constants import sockets
from ..base_node import SN_BaseNode


class SN_LabelNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_LabelNode"
    bl_label = "Label"

    def on_create(self):
        self.add_input(sockets.INTERFACE)
        self.add_input(sockets.STRING, "Label")

    def generate(self, context):
        self.code = f"""
            self.layout.label(text={self.inputs['Label'].code()})
        """
