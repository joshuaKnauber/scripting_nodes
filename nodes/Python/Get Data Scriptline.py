import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_GetDataScriptlineNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetDataScriptlineNode"
    bl_label = "Get Data Scriptline"
    bl_width_default = 200

    def on_create(self, context):
        self.add_string_input("Line")
        self.add_data_output("Data").changeable = True
        
    def evaluate(self, context):
        self.outputs[0].python_value = f"eval({self.inputs[0].python_value})"