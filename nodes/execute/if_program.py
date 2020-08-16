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
        next_code = ""
        if self.outputs[0].is_linked:
            next_code = self.outputs[0].links[0].to_socket

        do_code = ""
        if self.outputs[1].is_linked:
            do_code = self.outputs[1].links[0].to_socket
        if do_code == "":
            do_code = "pass"

        else_code = ""
        if self.outputs[2].is_linked:
            else_code = self.outputs[2].links[0].to_socket
        if else_code == "":
            else_code = "pass"

        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["if ", input_data[1]["code"], ":"]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                        [do_code]
                    ]
                },
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["else:"]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                        [else_code]
                    ]
                },
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        [next_code]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": []
        }
