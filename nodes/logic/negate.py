#SN_NegateNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_NegateNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_NegateNode"
    bl_label = "Negate"
    bl_icon = "FORCE_CHARGE"
    node_color = (0.65,0,0)
    bl_width_default = 110
    should_be_registered = False

    def inititialize(self,context):
        self.sockets.create_input(self,"BOOLEAN","Value")
        self.sockets.create_output(self,"BOOLEAN","Output")

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
