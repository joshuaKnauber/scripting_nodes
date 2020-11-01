#SN_CombineVectorNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_CombineVectorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CombineVectorNode"
    bl_label = "Combine Vector"
    bl_icon = "LINKED"
    node_color = (0.125,0.125,0.125)
    should_be_registered = False

    docs = {
        "text": ["This node is used to <important>combine numbers into a vector</>.",
                "Use Four Numbers: <subtext>The input vector has four numbers</>",
                ""],
        "python": ["(1.0,2.0,3.0)"]

    }

    def update_four(self,context):
        self.outputs[0].use_four_numbers = self.use_four
        if self.use_four:
            if len(self.inputs) == 3:
                self.sockets.create_input(self,"FLOAT","W")
        else:
            if len(self.inputs) == 4:
                self.sockets.remove_input(self,self.inputs[-1])

    use_four: bpy.props.BoolProperty(default=False,name="Use Four Numbers", update=update_four)

    def inititialize(self,context):
        self.sockets.create_input(self,"FLOAT","X")
        self.sockets.create_input(self,"FLOAT","Y")
        self.sockets.create_input(self,"FLOAT","Z")
        self.sockets.create_output(self,"VECTOR","Value")

    def draw_buttons(self, context, layout):
        layout.prop(self,"use_four")

    def evaluate(self, socket, node_data, errors):

        vector = ["(",node_data["input_data"][0]["code"],",",node_data["input_data"][1]["code"],",",node_data["input_data"][2]["code"]]
        if self.use_four:
            vector += [",",node_data["input_data"][3]["code"],")"]
        else:
            vector += [")"]
        
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        vector
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }