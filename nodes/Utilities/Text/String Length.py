import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_StringLengthNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_StringLengthNode"
    bl_label = "String Length"
    node_color = "STRING"
    bl_width_default = 200

    def on_create(self, context):
        self.add_string_input("String")
        self.add_integer_output("Length")

    def evaluate(self, context):
        self.outputs["Length"].python_value = f"len({self.inputs[0].python_value})"