#SN_DiceNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_DiceNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DiceNode"
    bl_label = "Dice"
    bl_icon = "MESH_CUBE"
    node_color = (0.2,0.4,0.75)
    should_be_registered = False

    docs = {
        "text": ["This node is used as a <important>random number input</>.",
                ""],
        "python": ["import random",
                "random.randint(<number>0</>, <number>5</>)"]

    }

    def inititialize(self,context):
        self.sockets.create_output(self,"INTEGER","Value")

    def evaluate(self, socket, node_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["random.randint(1,6)"]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }

    def required_imports(self):
        return ["random"]
