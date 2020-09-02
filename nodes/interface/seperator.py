#SN_SeperatorNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_SeperatorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SeperatorNode"
    bl_label = "Seperator"
    bl_icon = "LINENUMBERS_OFF"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")
        factor = self.sockets.create_input(self, "FLOAT", "Factor")
        factor.set_value(1)

    def evaluate(self, socket, node_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }
