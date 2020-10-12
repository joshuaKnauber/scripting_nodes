#SN_RepeatProgramNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_RepeatProgramNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RepeatProgramNode"
    bl_label = "Repeat (Program)"
    bl_icon = "FILE_REFRESH"
    node_color = (0.2, 0.2, 0.2)
    should_be_registered = False

    docs = {
        "text": ["The repeat node is used to <important>repeat a certain block of nodes a number of times</>.",
                "",
                "Repetitions Input: <subtext>The number of times the nodes get executed</>",
                "Repeat Output: <subtext>Whatever is connected here will be repeated, can be any number of execute nodes</>",
                "Step Output: <subtext>The current index of the step starting at 0</>"],
        "python": ["<function>for</> Step in <function>range</>( <number>5</> ):",
                   "    <function>print</>( \"test\" )",
                   "    <function>print</>( Step )"]
    }

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

    def evaluate(self, socket, node_data, errors):
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
                "errors": errors
            }
        # return the code block and next output
        else:
            next_code = ""
            if node_data["output_data"][0]["code"]:
                next_code = node_data["output_data"][0]["code"]

            output = ""
            if node_data["output_data"][1]["code"]:
                output = node_data["output_data"][1]["code"]

            return {
                "blocks": [
                    {
                        "lines": [ # lines is a list of lists, where the lists represent the different lines
                            [self.var_name + " = 0"],
                            ["for " + self.var_name + " in range(", node_data["input_data"][1]["code"], "):"]
                        ],
                        "indented": [ # indented is a list of lists, where the lists represent the different lines
                            ["pass"],
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
                "errors": errors
            }

