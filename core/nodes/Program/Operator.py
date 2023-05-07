import bpy
from ..base_node import SN_BaseNode


class SN_OperatorNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_OperatorNode"
    bl_label = "Operator"

    def on_create(self, context):
        self.add_execute_output()
