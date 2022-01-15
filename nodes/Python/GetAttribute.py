import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.GetDataNode import GetDataNode



class SN_GetPropertyScriptlineNode(bpy.types.Node, SN_ScriptingBaseNode, GetDataNode):

    bl_idname = "SN_GetPropertyScriptlineNode"
    bl_label = "Get Property Scriptline"
    bl_width_default = 200

    def on_create(self, context):
        self.add_blend_data_input()
        self.add_string_input("Property")
        self.add_data_output("Data")
        
    def evaluate(self, context):
        self.outputs[0].python_value = f"getattr({self.inputs[0].python_value}, {self.inputs['Property'].python_value}, None)"
        
    def draw_node(self, context, layout):
        self.draw_data_select(layout)