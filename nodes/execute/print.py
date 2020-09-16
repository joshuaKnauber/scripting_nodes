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
        "text": ["The print node is used to <important>write things to the console</>.",
                "",
                "Value Inputs: <subtext>What is connected here will be printed.</>",
                "<subtext>                   This can be any type of data like </>numbers, strings, etc."],
        "python": ["<function>print</>( <string>\"my example\"</>, <number>123</>, <string>\"test\"</> )"]
    }

    def inititialize(self,context):
        self.sockets.create_input(self,"EXECUTE","Execute")
        self.sockets.create_input(self,"DATA","Value",True)
        self.sockets.create_output(self,"EXECUTE","Execute")

    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if node_data["output_data"][0]["code"]:
            next_code = node_data["output_data"][0]["code"]
        
        print_text = []
        for socket in node_data["input_data"]:
            if socket["name"] == "Value" and socket["code"] != None and socket["code"] != "None":
                print_text += [",", socket["code"]]
        if print_text:
            print_text = print_text[1:]

        return {
            "blocks": [
                {
                    "lines": [
                        ["sn_print("] + print_text + [")"]
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
