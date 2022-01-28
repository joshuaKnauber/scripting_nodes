import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_HasAttributeNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_HasAttributeNode"
    bl_label = "Has Attribute"
    bl_width_default = 200

    def on_create(self, context):
        self.add_property_input()
        self.add_string_input("Attribute")
        self.add_boolean_output("Has Attribute")
        
    def evaluate(self, context):
        self.outputs[0].python_value = f"hasattr({self.inputs[0].python_value}, {self.inputs['Attribute'].python_value})"