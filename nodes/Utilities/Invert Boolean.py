import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_InvertBooleanNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_InvertBooleanNode"
    bl_label = "Invert Boolean"
    node_color = "BOOLEAN"

    def on_create(self, context):
        self.add_boolean_input("Boolean")
        self.add_boolean_output("Boolean")

    def evaluate(self, context):
        self.outputs[0].python_value = f"not {self.inputs[0].python_value}"