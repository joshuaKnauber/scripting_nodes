import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons


class SN_NumberNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Outputs a number'''
    bl_idname = 'SN_NumberNode'
    bl_label = "Number"
    bl_icon = node_icons["INPUT"]  #<-- see node_looks.py

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INPUT"]  #<-- see node_looks.py

        self.outputs.new('SN_NumberSocket', "Value")

    
    def draw_buttons(self, context, layout):
        pass# draws extra buttons on node without inputs