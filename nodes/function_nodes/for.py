import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons

class SN_ForNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''For Node for running functions for every element'''
    bl_idname = 'SN_ForNode'
    bl_label = "For"
    bl_icon = node_icons["PROGRAM"]

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["PROGRAM"]

        inp = self.inputs.new('SN_ProgramSocket', "Program")
        inp.display_shape = "DIAMOND"

        inp = self.inputs.new('SN_SceneDataSocket', "Scene Data")
        inp.display_shape = "SQUARE"

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass

    def draw_buttons(self, context, layout):
        pass

    def evaluate(self,output):

        return {
                "code": [],
                "indented_blocks": [
                    {
                        "code": ["for ", value, ":\n"],
                        "function_node": do_next_node
                    }
                ]
                }
