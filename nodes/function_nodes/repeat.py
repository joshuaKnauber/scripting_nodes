import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons

class SN_RepeatNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Repeat node for repeating a task'''
    bl_idname = 'SN_RepeatNode'
    bl_label = "Repeat"
    bl_icon = node_icons["FUNCTION"]

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["FUNCTION"]

        inp = self.inputs.new('SN_ProgramSocket', "Program")
        inp.display_shape = "DIAMOND"

        self.inputs.new('SN_NumberSocket', "Value")

        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

        repeat = self.outputs.new('SN_ProgramSocket', "Repeat")
        repeat.display_shape = "DIAMOND"

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

        repeat_next_node = None
        if self.outputs[1].is_linked:
            repeat_next_node = self.outputs[1].links[0].to_node

        return {
                "code": [],
                "indented_blocks": [
                    {
                        "code": ["for i in range(abs(int(", value, "))):\n"],
                        "function_node": repeat_next_node
                    }
                ]
                }
