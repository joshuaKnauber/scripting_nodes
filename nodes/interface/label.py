#SN_LabelNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_LabelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_LabelNode"
    bl_label = "Label"
    bl_icon = "SORTALPHA"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    def inititialize(self,context):
        self.sockets.create_input(self,"STRING","String")
        self.sockets.create_output(self,"LAYOUT","Layout")

    def draw_buttons(self,context,layout):
        pass

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

    def required_imports(self):
        return []
