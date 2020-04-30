import bpy


class SN_ScriptingBaseNode:
    bl_width_min = 40
    bl_width_default = 160
    bl_width_max = 5000
    _isScriptingNode = True

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SN_ScriptingNodesTree'

    def update(self):
        pass


#Example Node
"""
import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons


class SN_NodeName(bpy.types.Node, SN_ScriptingBaseNode):
    '''Description for what the node does'''
    bl_idname = 'SN_NodeName'
    bl_label = "Label of the node"
    bl_icon = node_icons["node_type"]  #<-- see node_looks.py

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["node_type"]  #<-- see node_looks.py

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
"""