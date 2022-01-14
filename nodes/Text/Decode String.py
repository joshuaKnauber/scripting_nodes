import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_DecodeStringNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DecodeStringNode"
    bl_label = "Decode Byte String"
    node_color = "STRING"

    def on_create(self, context):
        self.add_string_input("Bytes")
        self.add_string_output("String")

    def evaluate(self, context):
        self.outputs[0].python_value = f"{self.inputs['Bytes'].python_value}.decode('utf-8') "