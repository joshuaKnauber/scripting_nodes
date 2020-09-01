#SN_CreateOperator

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_CreateOperator(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CreateOperator"
    bl_label = "Operator"
    bl_icon = "MEMORY"
    bl_width_default = 250
    node_color = (0.65,0,0)
    should_be_registered = True

    label: bpy.props.StringProperty(default="My Operator",name="Label",description="Label of the operator")
    description: bpy.props.StringProperty(default="My Operators description",name="Description",description="Description of the operator shown in tooltips")

    def inititialize(self,context):
        self.sockets.create_input(self,"BOOLEAN","Run Condition")
        self.sockets.create_output(self,"EXECUTE","Execute")

    def draw_buttons(self, context, layout):
        layout.prop(self,"label")
        layout.prop(self,"description")

    def evaluate(self, socket, node_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        [self.outputs[0].links[0].to_socket]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }
