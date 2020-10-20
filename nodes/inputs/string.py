#SN_StringNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_StringNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_StringNode"
    bl_label = "String"
    bl_icon = "CON_TRANSFORM"
    node_color = (0,0.75,0)
    should_be_registered = False

    docs = {
        "text": ["This node is used as a <important>string input</>.",
                ""],
        "python": ["<string>\"Hello There\"</>"]

    }

    string_value: bpy.props.StringProperty(name="Value")

    def inititialize(self,context):
        self.sockets.create_output(self,"STRING","Value")

    def draw_buttons(self, context, layout):
        layout.prop(self, "string_value", text="")

    def evaluate(self, socket, node_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["r\"" + self.string_value + "\""]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }
