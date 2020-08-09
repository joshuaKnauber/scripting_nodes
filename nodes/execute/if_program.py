#SN_IfProgramNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_IfProgramNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IfProgramNode"
    bl_label = "If (Program)"
    bl_icon = "CON_ACTION"
    node_color = (0.2, 0.2, 0.2)
    should_be_registered = False

    def inititialize(self,context):
        self.sockets.create_input(self,"EXECUTE","Execute")
        self.sockets.create_input(self,"BOOLEAN","Value")
        self.sockets.create_output(self,"EXECUTE","Execute")
        self.sockets.create_output(self,"EXECUTE","Do")
        self.sockets.create_output(self,"EXECUTE","Else")

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
