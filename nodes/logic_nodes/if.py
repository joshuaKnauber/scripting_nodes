import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons

class SN_IfNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''If Node for spliting to do and else'''
    bl_idname = 'SN_IfNode'
    bl_label = "If"
    bl_icon = node_icons["LOGIC"]

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["LOGIC"]

        inp = self.inputs.new('SN_ProgramSocket', "Program")
        inp.display_shape = "DIAMOND"

        self.inputs.new('SN_BooleanSocket', "Value")

        out = self.outputs.new('SN_ProgramSocket', "Continue")
        out.display_shape = "DIAMOND"

        do = self.outputs.new('SN_ProgramSocket', "Do")
        do.display_shape = "DIAMOND"
        els = self.outputs.new('SN_ProgramSocket', "Else")
        els.display_shape = "DIAMOND"

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass

    def draw_buttons(self, context, layout):
        pass

    def evaluate(self,output):
        value1 = str(self.inputs[0])

        if self.inputs[0].is_linked:
            value1 = self.inputs[0].links[0].from_socket

        return {"code": ["if", " ", value1, ": "]}
