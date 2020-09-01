#SN_PrintNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_PrintNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PrintNode"
    bl_label = "Print"
    bl_icon = "CONSOLE"
    node_color = (0.2, 0.2, 0.2)
    should_be_registered = False

    docs = {
        "text": ["The print node is used to <red>write things to the console</>.",
                "",
                "It will print what is connected to its <red>value input</>.",
                "This can be any type of data like <data>numbers, strings, etc.</>"],
        "python": ["<function>print</>(<data>  value  </>)"]
    }

    def inititialize(self,context):
        self.sockets.create_input(self,"EXECUTE","Execute")
        self.sockets.create_input(self,"DATA","Value")
        self.sockets.create_output(self,"EXECUTE","Execute")

    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if self.outputs[0].is_linked:
            next_code = self.outputs[0].links[0].to_socket
        
        print_text = ""
        if input_data[1]["code"] != "None":
            print_text = input_data[1]["code"]

        return {
            "blocks": [
                {
                    "lines": [
                        ["print(", print_text ,")"]
                    ],
                    "indented": [
                    ]
                },
                {
                    "lines": [
                        [next_code]
                    ],
                    "indented": [
                    ]
                }
            ],
            "errors": errors
        }
