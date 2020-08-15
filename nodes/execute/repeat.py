#SN_RepeatProgramNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_RepeatProgramNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RepeatProgramNode"
    bl_label = "Repeat (Program)"
    bl_icon = "CON_ACTION"
    node_color = (0.2, 0.2, 0.2)
    should_be_registered = False

    def inititialize(self,context):
        self.var_name = self.get_var_name()

        self.sockets.create_input(self,"EXECUTE","Execute")
        self.sockets.create_input(self,"INTEGER","Repetitions")
        self.sockets.create_output(self,"EXECUTE","Execute")
        self.sockets.create_output(self,"EXECUTE","Repeat")
        self.sockets.create_output(self,"INTEGER","Step")

    def get_var_name(self):
        highest_var_name = 0
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname == self.bl_idname:
                number = int(node.var_name.split("_")[-1])
                highest_var_name = max(number,highest_var_name)
        return "repeat_execute_node_"+str(highest_var_name + 1)

    var_name: bpy.props.StringProperty(default="repeat_execute_node_0")

    def copy(self, node):
        self.var_name = self.get_var_name()

    def evaluate(self, socket, input_data, errors):
        # return the name of the variable
        if socket == self.outputs[2]:
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
                "errors": []
            }
        # return the code block and next output
        else:
            next_code = ""
            if self.outputs[0].is_linked:
                next_code = self.outputs[0].links[0].to_socket

            output = ""
            if self.outputs[1].is_linked:
                output = self.outputs[1].links[0].to_socket

            if output == "":
                output = "pass"
            return {
                "blocks": [
                    {
                        "lines": [ # lines is a list of lists, where the lists represent the different lines
                            [self.var_name + " = 0"],
                            ["for " + self.var_name + " in range(", input_data[1]["code"], "):"]
                        ],
                        "indented": [ # indented is a list of lists, where the lists represent the different lines
                            [output]
                        ]
                    },
                    {
                        "lines": [ # lines is a list of lists, where the lists represent the different lines
                            [next_code]
                        ],
                        "indented": [ # indented is a list of lists, where the lists represent the different lines
                        ]
                    }
                ],
                "errors": []
            }

