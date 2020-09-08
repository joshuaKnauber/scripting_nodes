#SN_VectorNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_VectorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_VectorNode"
    bl_label = "Vector"
    bl_icon = "CON_TRANSFORM"
    node_color = (0.6,0.2,0.8)
    should_be_registered = False

    def update_four(self, context):
        self.outputs[0].use_four_numbers = self.use_four_numbers

    value: bpy.props.FloatVectorProperty(default=(0,0,0),name="Value",description="Value of this variable")
    four_value: bpy.props.FloatVectorProperty(default=(0,0,0,0),size=4,name="Value",description="Value of this variable")
    use_four_numbers: bpy.props.BoolProperty(default=False,name="Use Four Numbers", description="Outputs a vector with four numbers instead of three", update=update_four)

    def inititialize(self,context):
        self.sockets.create_output(self,"VECTOR","Value")

    def draw_buttons(self, context, layout):
        col = layout.column(align=True)
        col.label(text="Value:")
        if self.use_four_numbers:
            col.prop(self,"four_value",text="")
        else:
            col.prop(self,"value",text="")
        layout.prop(self,"use_four_numbers")

    def evaluate(self, socket, node_data, errors):
        vector = (self.value[0], self.value[1], self.value[2])
        if self.use_four_numbers:
            vector = (self.four_value[0], self.four_value[1], self.four_value[2], self.four_value[3])
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        [str(vector)]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }
