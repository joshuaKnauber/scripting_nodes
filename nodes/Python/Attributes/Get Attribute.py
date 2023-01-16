import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_GetAttributeNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_GetAttributeNode"
    bl_label = "Get Attribute"
    bl_width_default = 200

    def on_create(self, context):
        self.add_data_input()
        self.add_string_input("Attribute")
        self.add_data_input("Fallback")
        self.add_data_output("Data").changeable = True
        
    def evaluate(self, context):
        self.outputs[0].python_value = f"getattr({self.inputs[0].python_value}, {self.inputs['Attribute'].python_value}, {self.inputs['Fallback'].python_value})"