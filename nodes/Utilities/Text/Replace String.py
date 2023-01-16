import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_ReplaceStringNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_ReplaceStringNode"
    bl_label = "Replace in String"
    node_color = "STRING"
    bl_width_default = 200

    def on_create(self, context):
        self.add_string_input("String")
        self.add_string_input("Old")
        self.add_string_input("New")
        self.add_string_output("String")

    def evaluate(self, context):
        self.outputs[0].python_value = f"{self.inputs[0].python_value}.replace({self.inputs[1].python_value}, {self.inputs[2].python_value})"