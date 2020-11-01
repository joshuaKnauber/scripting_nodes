#SN_SplitVectorNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_SplitVectorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SplitVectorNode"
    bl_label = "Split Vector"
    bl_icon = "UNLINKED"
    node_color = (0.125,0.125,0.125)
    should_be_registered = False

    docs = {
        "text": ["This node is used to <important>split a vector into its values</>.",
                "Use Four Numbers: <subtext>The input vector has four numbers</>",
                ""],
        "python": ["(1.0,2.0,3.0)[0]"]

    }

    def update_four(self,context):
        self.inputs[0].use_four_numbers = self.use_four
        if self.use_four:
            if len(self.outputs) == 3:
                self.sockets.create_output(self,"FLOAT","W")
        else:
            if len(self.outputs) == 4:
                self.sockets.remove_output(self,self.outputs[-1])

    use_four: bpy.props.BoolProperty(default=False,name="Use Four Numbers", update=update_four)

    def inititialize(self,context):
        self.sockets.create_input(self,"VECTOR","Value")
        self.sockets.create_output(self,"FLOAT","X")
        self.sockets.create_output(self,"FLOAT","Y")
        self.sockets.create_output(self,"FLOAT","Z")

    def draw_buttons(self, context, layout):
        layout.prop(self,"use_four")

    def evaluate(self, socket, node_data, errors):

        out_index = 0
        for i in range(len(self.outputs)):
            if socket == self.outputs[i]:
                out_index = i
        
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        [node_data["input_data"][0]["code"], "[",str(out_index),"]"]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }