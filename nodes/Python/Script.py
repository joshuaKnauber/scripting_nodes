import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_ScriptNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_ScriptNode"
    bl_label = "Script"
    node_color = "PROGRAM"
    is_trigger = True
    bl_width_default = 200


    def on_create(self, context):
        self.add_execute_output()

    def evaluate(self, context):
        self.code = self.indent(self.outputs[0].python_value, 0)