#SN_BooleanNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_BooleanNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BooleanNode"
    bl_label = "Boolean"
    bl_icon = "CON_TRANSFORM"
    node_color = (0.65,0,0)
    should_be_registered = False

    docs = {
        "text": ["This node is used as an <important>boolean input</>.",
                "This means it can be either <red>True</> or <red>False</>",
                ""],
        "python": ["<red>True</> or <red>False</>"]

    }

    bool_value: bpy.props.BoolProperty(name="Value")

    def inititialize(self,context):
        self.sockets.create_output(self,"BOOLEAN","Value")

    def draw_buttons(self, context, layout):
        layout.prop(self, "bool_value", text=str(self.bool_value), toggle=True)

    def evaluate(self, socket, node_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        [str(self.bool_value)]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }
