import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_PadStringNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PadStringNode"
    bl_label = "Pad String"
    node_color = "STRING"
    bl_width_default = 200

    def on_create(self, context):
        self.add_string_input("String")
        self.add_integer_input("Size")
        self.add_string_input("Pad")
        self.add_string_output("Padded String")

    def evaluate(self, context):
        self.outputs["Padded String"].python_value = f"{self.inputs['String'].python_value}.rjust({self.inputs['Size'].python_value}, {self.inputs['Pad'].python_value})"