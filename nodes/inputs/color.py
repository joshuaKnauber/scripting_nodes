#SN_ColorNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_ColorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ColorNode"
    bl_label = "Color"
    bl_icon = "MATERIAL_DATA"
    node_color = (0.6,0.2,0.8)
    should_be_registered = False

    value: bpy.props.FloatVectorProperty(default=(0.5,0.5,0.5),subtype="COLOR",name="Value",min=0,max=1,description="Value of this variable")
    four_value: bpy.props.FloatVectorProperty(default=(0.5,0.5,0.5,1),subtype="COLOR",size=4,min=0,max=1,name="Value",description="Value of this variable")
    use_four_numbers: bpy.props.BoolProperty(default=False,name="Use alpha channel", description="Outputs a vector with four numbers instead of three")

    def inititialize(self,context):
        self.sockets.create_output(self,"VECTOR","Color")

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
