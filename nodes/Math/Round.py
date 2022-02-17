import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_RoundNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RoundNode"
    bl_label = "Round Number"
    node_color = "FLOAT"

    def on_create(self, context):
        self.add_float_input("Value")
        self.add_integer_input("Decimals")
        self.add_float_output("Rounded Number")

    def evaluate(self, context):
        self.outputs[0].python_value = f"round({self.inputs['Value'].python_value}, abs({self.inputs['Decimals'].python_value}))"
