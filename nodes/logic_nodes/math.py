import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons


class SN_UiMathNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for basic math'''
    bl_idname = 'SN_UiMathNode'
    bl_label = "Math"
    bl_icon = node_icons["MATH"]

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["MATH"]

        self.inputs.new('SN_ENUMSocket', "FUNCTION")
        self.inputs.new('SN_INTSocket', "INPUT")
        self.inputs.new('SN_INTSocket', "INPUT2")
        self.outputs.new('SN_INTSocket', "OUTPUT")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        pass# draws extra buttons on node