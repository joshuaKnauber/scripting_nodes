#SN_PrintNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_PrintNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PrintNode"
    bl_label = "Print"
    bl_icon = "CONSOLE"
    node_color = (0.2, 0.2, 0.2)
    should_be_registered = False

    def inititialize(self,context):
        self.sockets.create_input(self,"EXECUTE","Execute")
        self.sockets.create_input(self,"DATA","Value")
        self.sockets.create_output(self,"EXECUTE","Execute")

    def evaluate(self, socket, input_data, errors):
        print_text = ""
        if input_data[1]["code"] != None:
            print_text = input_data[1]["code"]

        return {
            "blocks": [
                {
                    "lines": [
                        ["print(", print_text ,")"]
                    ],
                    "indented": [
                    ]
                }
            ],
            "errors": errors
        }
