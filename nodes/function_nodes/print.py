import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons


class SN_PrintNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for printing a value'''
    bl_idname = 'SN_PrintNode'
    bl_label = "Print"
    bl_icon = node_icons["FUNCTION"]

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["FUNCTION"]

        #Node Inputs
        inp = self.inputs.new('SN_ProgramSocket', "Program")
        inp.display_shape = "DIAMOND"

        self.inputs.new('SN_DataSocket', "Value")

        #Node Outputs
        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        pass# draws extra buttons on node without inputs

    def evaluate(self, output):
        if len(self.inputs["Value"].links) == 1:
            return {"code": ["print(", self.inputs["Value"].links[0].from_socket, ")"]}
        else:
            return{"code": ["print('')"], "error": 1}
