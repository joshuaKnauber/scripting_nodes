#SN_IntegerNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_IntegerNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IntegerNode"
    bl_label = "Integer"
    bl_icon = "CON_TRANSFORM"
    node_color = (0.2,0.4,0.75)
    bl_width_default = 160
    should_be_registered = False

    int_value: bpy.props.IntProperty(name="Value")

    def inititialize(self,context):
        self.sockets.create_output(self,"INTEGER","Output")

    def draw_buttons(self, context, layout):
        layout.prop(self, "int_value", text="")

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
