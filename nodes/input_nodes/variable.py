import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons


class SN_NodeName(bpy.types.Node, SN_ScriptingBaseNode):
    '''Description for what the node does'''
    bl_idname = 'SN_NodeName'
    bl_label = "Label of the node"
    bl_icon = node_icons["FUNCTION"]  #<-- see node_looks.py

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["FUNCTION"]  #<-- see node_looks.py

        #Node Inputs
        self.inputs.new('SN_StringSocket', "Text")

        #Node Outputs
        self.outputs.new('SN_StringSocket', "Text")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        pass# draws extra buttons on node without inputs
    
    def evaluate(self):
        pass# return function for compiler