import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_OperatorNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_OperatorNode"
    bl_label = "Operator"

    def on_create(self, context):
        self.add_execute_output()
