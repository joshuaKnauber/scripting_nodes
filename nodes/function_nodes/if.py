import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons

class SN_IfNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''If Node for spliting to do and else'''
    bl_idname = 'SN_IfNode'
    bl_label = "If"
    bl_icon = node_icons["FUNCTION"]

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["FUNCTION"]

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
        value = str(self.inputs[1].value)

        if self.inputs[1].is_linked:
            value = self.inputs[1].links[0].from_socket

        do_next_node = None
        if self.outputs[1].is_linked:
            do_next_node = self.outputs[1].links[0].to_node
        else_next_node = None
        if self.outputs[2].is_linked:
            else_next_node = self.outputs[2].links[0].to_node

        return {
                "code": [],
                "indented_blocks": [
                    {
                        "code": ["if ", value, ":\n"],
                        "function_node": do_next_node
                    },
                    {
                        "code": ["else:\n"],
                        "function_node": else_next_node
                    }
                ]
                }
