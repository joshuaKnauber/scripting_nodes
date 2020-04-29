import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons

class SN_ToStringNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Converts the data input to a string output'''
    bl_idname = 'SN_ToStringNode'
    bl_label = "Data To Text"
    bl_icon = node_icons["LOGIC"]

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["LOGIC"] 

        self.inputs.new('SN_DataSocket', "Data")

        self.outputs.new('SN_StringSocket', "Text")

    
    def draw_buttons(self, context, layout):
        layout.prop(self,"number",text="")

    def evaluate(self, output):
        if self.inputs[0].is_linked:
            return {"code": ["str(",self.inputs[0].links[0].from_socket,")"]}
        else:
            return {"code": ["str('')"]}
        