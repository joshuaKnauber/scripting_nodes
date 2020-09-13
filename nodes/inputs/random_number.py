#SN_RandomNumberNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_RandomNumberNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RandomNumberNode"
    bl_label = "Random Number"
    bl_icon = "CON_TRANSFORM"
    node_color = (0.2,0.4,0.75)
    should_be_registered = False

    docs = {
        "text": ["This node is used as a <important>random number input</>.",
                ""],
        "python": ["import random",
                "random.randint(<number>0</>, <number>5</>)"]

    }

    def update_socket(self, context):
        if self.use_float:
            self.color = (0.23,0.65,0.75)
            if self.outputs[0].bl_idname != "SN_FloatSocket":
                self.sockets.change_socket_type(self, self.inputs[0], "FLOAT")
                self.sockets.change_socket_type(self, self.inputs[1], "FLOAT")
                self.sockets.change_socket_type(self, self.outputs[0], "FLOAT")
        else:
            self.color = (0.2,0.4,0.75)
            if self.outputs[0].bl_idname != "SN_IntSocket":
                self.sockets.change_socket_type(self, self.inputs[0], "INTEGER")
                self.sockets.change_socket_type(self, self.inputs[1], "INTEGER")
                self.sockets.change_socket_type(self, self.outputs[0], "INTEGER")

    use_float: bpy.props.BoolProperty(name="Use float", description="Get a float node", update=update_socket, default=False)

    def inititialize(self,context):
        self.sockets.create_output(self,"INTEGER","Value")
        self.sockets.create_input(self, "INTEGER", "Min")
        self.sockets.create_input(self, "INTEGER", "Max")

    def draw_buttons(self, context, layout):
        if self.use_float:
            text = "Float"
        else:
            text = "Integer"
        layout.prop(self, "use_float", toggle=True, text=text)

    def evaluate(self, socket, node_data, errors):
        randtype = "randint"
        if self.use_float:
            randtype = "uniform"

        from_to = node_data["input_data"][0]["code"] + ", " + node_data["input_data"][1]["code"]
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["random." + randtype + "(min(", from_to, "), max(", from_to, "))"]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }

    def required_imports(self):
        return ["random"]
