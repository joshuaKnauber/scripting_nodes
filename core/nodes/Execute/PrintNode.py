import bpy

from ....constants import sockets
from ..base_node import SN_BaseNode


class SN_PrintNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_PrintNode"
    bl_label = "Print"

    def on_create(self):
        self.add_input(sockets.EXECUTE)
        self.add_input(sockets.STRING, "Text")
        self.add_output(sockets.EXECUTE)

    def generate(self, context):
        self.require_register = True
        self.code = f"""
print({self.inputs["Text"].code()})
{self.outputs["Execute"].code(2)}
"""
