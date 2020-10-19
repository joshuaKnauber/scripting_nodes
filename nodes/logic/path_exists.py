#SN_PathExistsNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_PathExistsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PathExistsNode"
    bl_label = "Path Exists"
    bl_icon = "FORCE_CHARGE"
    node_color = (0.125,0.125,0.125)
    bl_width_default = 100
    should_be_registered = False

    docs = {
        "text": ["This node is used to <important>check if a filepath exists</>.",
                ""],
        "python": ["os.path.exists(<string>filepath</>)"]

    }

    def inititialize(self,context):
        self.sockets.create_input(self,"STRING","Path")
        self.sockets.create_output(self,"BOOLEAN","Output")

    def evaluate(self, socket, node_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["os.path.exists(",node_data["input_data"][0]["code"],")"]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }

    def required_imports(self):
        return ["os"]

