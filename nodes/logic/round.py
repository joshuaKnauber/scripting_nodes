#SN_RoundNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_RoundNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RoundNode"
    bl_label = "Round"
    bl_icon = "CON_TRANSLIKE"
    node_color = (0.125,0.125,0.125)
    should_be_registered = False

    docs = {
        "text": ["This node is used to <important>round a float value</>.",
                ""],
        "python": ["<function>round</>(<float>3.45678</>,<integer>2</>)"]

    }

    def inititialize(self,context):
        self.sockets.create_input(self,"FLOAT","Value")
        self.sockets.create_input(self,"INTEGER","Decimals")
        self.sockets.create_output(self,"FLOAT","Output")

    def evaluate(self, socket, node_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["round(", node_data["input_data"][0]["code"], ", abs(", node_data["input_data"][1]["code"], "))"]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }
