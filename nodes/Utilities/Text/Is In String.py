import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_IsInStringNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IsInStringNode"
    bl_label = "Substring is in String"
    node_color = "STRING"
    bl_width_default = 200

    def on_create(self, context):
        self.add_string_input("String")
        self.add_string_input("Substring")
        self.add_boolean_output("Is in String")

    def evaluate(self, context):
        self.outputs[0].python_value = f"{self.inputs['Substring'].python_value} in {self.inputs['String'].python_value}"