import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_SliceStringNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_SliceStringNode"
    bl_label = "Slice String"
    node_color = "STRING"
    bl_width_default = 200

    def on_create(self, context):
        self.add_string_input("String")
        self.add_integer_input("Index")
        self.add_string_output("Before")
        self.add_string_output("After")

    def evaluate(self, context):
        self.outputs["Before"].python_value = f"{self.inputs['String'].python_value}[:{self.inputs['Index'].python_value}]"
        self.outputs["After"].python_value = f"{self.inputs['String'].python_value}[{self.inputs['Index'].python_value}:]"