#SN_IfProgramNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_IfProgramNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IfProgramNode"
    bl_label = "If (Program)"
    bl_icon = "SNAP_EDGE"
    node_color = (0.2, 0.2, 0.2)
    should_be_registered = False

    docs = {
        "text": ["The If Node is used to <important>do two different things depending on the input</>.",
                "",
                "Value Input: <subtext>If True 'Do' gets executed, if False 'Else' gets executed</>"],
        "python": ["if <number>5</> < <number>10</>:",
                   "    <function>print</>(\"True\")",
                   "else:",
                   "    <function>print</>(\"False\")"]

    }


    def inititialize(self,context):
        self.sockets.create_input(self,"EXECUTE","Execute")
        self.sockets.create_input(self,"BOOLEAN","Value")
        self.sockets.create_output(self,"EXECUTE","Execute")
        self.sockets.create_output(self,"EXECUTE","Do")
        self.sockets.create_output(self,"EXECUTE","Else")

    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if node_data["output_data"][0]["code"]:
            next_code = node_data["output_data"][0]["code"]

        do_code = ""
        if node_data["output_data"][1]["code"]:
            do_code = node_data["output_data"][1]["code"]

        else_code = ""
        if node_data["output_data"][2]["code"]:
            else_code = node_data["output_data"][2]["code"]

        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["if ", node_data["input_data"][1]["code"], ":"]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                        ["pass"],
                        [do_code]
                    ]
                },
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["else:"]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                        ["pass"],
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
            "errors": errors
        }
