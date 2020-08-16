#SN_CombineTextNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_CombineTextNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CombineTextNode"
    bl_label = "Combine Text"
    bl_icon = "PLUS"
    node_color = (0.65,0,0)
    should_be_registered = False

    def inititialize(self,context):
        self.sockets.create_input(self,"STRING","Value")
        self.sockets.create_input(self,"STRING","Value")
        self.sockets.create_output(self,"STRING","Output")

    def evaluate(self, socket, input_data, errors):
        text_one = input_data[0]["code"]
        if type(text_one) == str:
            text_one = "'" + input_data[0]["code"] + "'"

        text_two = input_data[1]["code"]
        if type(text_two) == str:
            text_two = "'" + input_data[1]["code"] + "'"

        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        [text_one, " + ", text_two]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": []
        }
