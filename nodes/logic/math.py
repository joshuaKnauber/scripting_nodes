#SN_MathNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_MathNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_MathNode"
    bl_label = "Math"
    bl_icon = "CON_TRANSLIKE"
    node_color = (0.125,0.125,0.125)
    should_be_registered = False

    docs = {
        "text": ["This node is used to <important>do math operations</>."
                ""],
        "python": ["<number>8</> * <number>4</>"]

    }

    operation: bpy.props.EnumProperty(items=[("+", "Add", "Add two numbers"), ("-", "Subtract", "Subtract two numbers"), ("*", "Multiply", "Multiply two numbers"), ("/", "Divide", "Divide two numbers")],name="Operation", description="The operation you want to commence")

    def inititialize(self,context):
        self.sockets.create_input(self,"FLOAT","Value")
        self.sockets.create_input(self,"FLOAT","Value")
        self.sockets.create_output(self,"FLOAT","Output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "operation", text="")

    def evaluate(self, socket, node_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["(", node_data["input_data"][0]["code"], self.operation, node_data["input_data"][1]["code"], ")"]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }
