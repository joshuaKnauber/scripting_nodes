import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_SetAttributeNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SetAttributeNode"
    bl_label = "Set Attribute"
    bl_width_default = 200

    # TODO
    def on_create(self, context):
        self.add_property_input()
        self.add_string_input("Property")
        self.add_data_output("Data").changeable = True
        
    def evaluate(self, context):
        self.outputs[0].python_value = f"getattr({self.inputs[0].python_value}, {self.inputs['Property'].python_value}, None)"