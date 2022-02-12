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
        
    def draw_node(self, context, layout):
        if self.outputs[0].bl_label == "Property" or self.outputs[0].bl_label == "Collection Property":
            layout.label(text="Use Get Property Scriptline for transformable properties!", icon="INFO")