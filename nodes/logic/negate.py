#SN_NegateNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_NegateNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_NegateNode"
    bl_label = "Negate"
    bl_icon = "FORCE_CHARGE"
    node_color = (0.125,0.125,0.125)
    bl_width_default = 100
    should_be_registered = False

    def inititialize(self,context):
        self.sockets.create_input(self,"BOOLEAN","Value")
        self.sockets.create_output(self,"BOOLEAN","Output")

    def evaluate(self, socket, node_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["not ", node_data["input_data"][0]["code"]]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }
