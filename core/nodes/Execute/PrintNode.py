import bpy

from ....constants import sockets
from ..base_node import SNA_BaseNode


class SNA_NodePrint(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodePrint"
    bl_label = "Print"

    def on_create(self):
        self.add_input(sockets.EXECUTE)
        self.add_input(sockets.STRING, "Text")
        self.add_output(sockets.EXECUTE)

    def generate(self, context):
        self.require_register = True
        self.code = f"""
print({self.inputs["Text"].get_code()})
{self.outputs["Execute"].get_code(2)}
"""
