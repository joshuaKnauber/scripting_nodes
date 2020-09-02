#SN_CompareNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_CompareNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CompareNode"
    bl_label = "Compare"
    bl_icon = "CON_SAMEVOL"
    node_color = (0.65,0,0)
    should_be_registered = False

    operation: bpy.props.EnumProperty(items=[("==", "=", "Equal"), ("!=", "≠", "Not equal"), ("<", "<", "Smaller than"), (">", ">", "Bigger than"), ("<=", "≤", "Smaller or equal to"), (">=", "≥", "Bigger or equal to")],name="Operation", description="The operation you want to commence")

    def inititialize(self,context):
        self.sockets.create_input(self,"DATA","Value")
        self.sockets.create_input(self,"DATA","Value")
        self.sockets.create_output(self,"BOOLEAN","Output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "operation", text="")

    def evaluate(self, socket, node_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        [node_data["input_data"][0]["code"], self.operation, node_data["input_data"][1]["code"]]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }
