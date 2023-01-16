import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_EncodeStringNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_EncodeStringNode"
    bl_label = "Encode Byte String"
    node_color = "STRING"

    def on_create(self, context):
        self.add_string_input("String")
        self.add_string_output("Bytes")

    def evaluate(self, context):
        self.outputs[0].python_value = f"{self.inputs['String'].python_value}.encode() "