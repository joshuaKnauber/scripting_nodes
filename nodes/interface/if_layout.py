#SN_IfLayoutNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_IfLayoutNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IfLayoutNode"
    bl_label = "If (Layout)"
    bl_icon = "SNAP_EDGE"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")
        self.sockets.create_input(self,"BOOLEAN","Value")
        self.sockets.create_output(self,"LAYOUT","Do")
        self.sockets.create_output(self,"LAYOUT","Else")

    def evaluate(self, socket, node_data, errors):
        do_layout = "pass"
        if node_data["output_data"][0]["code"]:
            do_layout = node_data["output_data"][0]["code"]

        else_layout = "pass"
        if node_data["output_data"][1]["code"]:
            else_layout = node_data["output_data"][1]["code"]

        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["if ", node_data["input_data"][1]["code"], ":"]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                        [do_layout]
                    ]
                },
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["else:"]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                        [else_layout]
                    ]
                }
            ],
            "errors": errors
        }


    def layout_type(self):
        if self.inputs[0].is_linked:
            if self.inputs[0].links[0].from_socket.bl_idname == self.inputs[0].bl_idname:
                return self.inputs[0].links[0].from_socket.node.layout_type()
        return "layout"