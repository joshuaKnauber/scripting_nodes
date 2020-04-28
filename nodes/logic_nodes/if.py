import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons


class SN_IfNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Outputs if and else based on boolean'''
    bl_idname = 'SN_IfNode'
    bl_label = "If"
    bl_icon = node_icons["LOGIC"]

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["LOGIC"]

        self.inputs.new('SN_BooleanSocket', "Input")

        self.outputs.new('SN_BooleanSocket', "Do")
        self.outputs.new('SN_BooleanSocket', "Else")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        pass# draws extra buttons on node without inputs
    
    def evaluate(self):
        pass