#SN_AndOrNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_AndOrNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AndOrNode"
    bl_label = "And/Or"
    bl_icon = "GRAPH"
    node_color = (0.125,0.125,0.125)
    should_be_registered = False

    docs = {
        "text": ["This node is used for <important>comparing two booleans</>.",
                ""],
        "python": ["<red>True</> and <red>False</>"]

    }

    andOr: bpy.props.EnumProperty(items=[(" and ", "And", "Both need to be true"), (" or ", "Or", "At least one needs to be true")],name="Operation", description="The operation you want to commence")

    def inititialize(self,context):
        self.sockets.create_input(self,"BOOLEAN","Value")
        self.sockets.create_input(self,"BOOLEAN","Value")
        self.sockets.create_output(self,"BOOLEAN","Output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "andOr", text="")

    def evaluate(self, socket, node_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        [node_data["input_data"][0]["code"], self.andOr, node_data["input_data"][1]["code"]]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }
