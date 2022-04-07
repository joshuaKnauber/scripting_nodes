import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_SetAttributeNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SetAttributeNode"
    bl_label = "Set Attribute"
    bl_width_default = 200

    def on_create(self, context):
        self.add_execute_input()
        self.add_data_input()
        self.add_string_input("Attribute")
        self.add_data_input("Value")
        self.add_execute_output()
        
    def evaluate(self, context):
        self.code = f"""
                    setattr({self.inputs[1].python_value}, {self.inputs['Attribute'].python_value}, {self.inputs['Value'].python_value})
                    {self.indent(self.outputs[0].python_value, 5)}
                    """
