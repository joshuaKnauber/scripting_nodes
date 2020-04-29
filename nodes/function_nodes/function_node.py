import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons


class SN_FunctionNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for starting a function'''
    bl_idname = 'SN_FunctionNode'
    bl_label = "Function"
    bl_icon = node_icons["FUNCTION"]

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["FUNCTION"]

        #Node Outputs
        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        pass# draws extra buttons on node without inputs

    def socket_value_update(self, context):
        print("socket update")

    def insert_link(self, link):
        pass

    def evaluate(self,output):
        next_node = None
        if len(self.outputs[0].links) > 0:
            next_node = self.outputs[0].links[0].to_node
        return {
                "code": [],
                "indented_blocks": [
                    {
                        "code": ["def testfunction():\n"],
                        "function_node": next_node
                    }
                ]
                }