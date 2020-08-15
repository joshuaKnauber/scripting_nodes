#SN_ButtonNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode

class SN_ButtonNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ButtonNode"
    bl_label = "Button"
    bl_icon = "SNAP_FACE"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")
        self.sockets.create_input(self,"STRING","Text")

    search_value: bpy.props.StringProperty(name="Search value", description="")

    def draw_buttons(self,context,layout):
        self.draw_icon_chooser(layout)

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
