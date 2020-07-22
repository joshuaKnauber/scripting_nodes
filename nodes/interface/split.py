#SN_SplitNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_SplitNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SplitNode"
    bl_label = "Split"
    bl_icon = "UV_ISLANDSEL"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")
        factor = self.sockets.create_input(self, "FLOAT", "Factor")
        factor.set_value(0.5)
        factor.use_factor = True
        self.sockets.create_output(self,"LAYOUT","Layout")
        self.sockets.create_output(self,"LAYOUT","Layout")

    def evaluate(self, socket, input_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": []
        }

    def layout_type(self):
        return "split"