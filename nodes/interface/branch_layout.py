#SN_BranchNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_BranchNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BranchNode"
    bl_label = "Branch (Layout)"
    bl_icon = "SORTALPHA"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")
        self.sockets.create_output(self,"LAYOUT","Layout", True)

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
