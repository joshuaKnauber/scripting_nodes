#SN_RepeatLayoutNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_RepeatLayoutNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RepeatLayoutNode"
    bl_label = "Repeat (Layout)"
    bl_icon = "CON_ACTION"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    def get_var_name(self):
        highest_var_name = 0
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname == self.bl_idname:
                number = int(node.var_name.split("_")[-1])
                highest_var_name = max(number,highest_var_name)
        return "repeat_layout_node_"+str(highest_var_name + 1)

    def inititialize(self,context):
        self.var_name = self.get_var_name()
        self.sockets.create_input(self,"LAYOUT","Layout")
        self.sockets.create_input(self,"INTEGER","Repetitions")
        self.sockets.create_output(self,"LAYOUT","Repeat")
        self.sockets.create_output(self,"INTEGER","Step")

    var_name: bpy.props.StringProperty(default="repeat_layout_node_0")

    def copy(self, node):
        self.var_name = self.get_var_name()

    def evaluate(self, socket, node_data, errors):
        if socket == self.outputs[1]:
            return {
                "blocks": [
                    {
                        "lines": [ # lines is a list of lists, where the lists represent the different lines
                            [self.var_name]
                        ],
                        "indented": [ # indented is a list of lists, where the lists represent the different lines
                        ]
                    }
                ],
                "errors": errors
            }
        else:
            output = "pass"
            if node_data["output_data"][0]["code"]:
                output = node_data["output_data"][0]["code"]

            return {
                "blocks": [
                    {
                        "lines": [ # lines is a list of lists, where the lists represent the different lines
                            [self.var_name + " = 0"],
                            ["for " + self.var_name + " in range(", node_data["input_data"][1]["code"], "):"]
                        ],
                        "indented": [ # indented is a list of lists, where the lists represent the different lines
                            [output]
                        ]
                    }
                ],
                "errors": errors
            }

    def layout_type(self):
        if self.inputs[0].is_linked:
            if self.inputs[0].links[0].from_socket.bl_idname == self.inputs[0].bl_idname:
                return self.inputs[0].links[0].from_socket.node.layout_type()
        return "layout"