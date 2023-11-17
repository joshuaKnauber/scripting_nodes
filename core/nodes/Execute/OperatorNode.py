import bpy

from ....constants import sockets
from ..base_node import SNA_BaseNode


class SNA_NodeOperator(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeOperator"
    bl_label = "Operator"

    def on_create(self):
        self.add_output(sockets.EXECUTE)

    def generate(self, context):
        self.require_register = True
        self.code = f"""
class SNA_OT_Operator_{self.id}(bpy.types.Operator):
    bl_idname = "sna.operator_{self.id}"
    bl_label = "My Operator"

    def execute(self, context):
        {self.outputs["Execute"].get_code(2)}
        return {{'FINISHED'}}
"""
