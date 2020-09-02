#SN_IfLayoutNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_IfLayoutNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IfLayoutNode"
    bl_label = "If (Layout)"
    bl_icon = "CON_ACTION"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")
        self.sockets.create_input(self,"BOOLEAN","Value")
        self.sockets.create_output(self,"LAYOUT","Do")
        self.sockets.create_output(self,"LAYOUT","Else")

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
