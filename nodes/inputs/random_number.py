#SN_RandomNumberNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_RandomNumberNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RandomNumberNode"
    bl_label = "Random Number"
    bl_icon = "CON_TRANSFORM"
    node_color = (0.2,0.4,0.75)
    should_be_registered = False

    def update_socket(self, context):
        if self.use_float:
            self.color = (0.23,0.65,0.75)
            if self.outputs[0].bl_idname != "SN_FloatSocket":
                self.sockets.change_socket_type(self, self.outputs[0], "FLOAT")
        else:
            self.color = (0.2,0.4,0.75)
            if self.outputs[0].bl_idname != "SN_IntSocket":
                self.sockets.change_socket_type(self, self.outputs[0], "INTEGER")

    use_float: bpy.props.BoolProperty(name="Use float", description="Get a float node", update=update_socket, default=False)

    def inititialize(self,context):
        self.sockets.create_output(self,"INTEGER","Value")

    def draw_buttons(self, context, layout):
        if self.use_float:
            text = "Float"
        else:
            text = "Integer"
        layout.prop(self, "use_float", toggle=True, text=text)

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
