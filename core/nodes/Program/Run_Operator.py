import bpy
from ..base_node import SN_BaseNode


class SN_RunOperatorNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RunOperatorNode"
    bl_label = "Run Operator"

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()

    def draw_node(self, context, layout):
        pass
