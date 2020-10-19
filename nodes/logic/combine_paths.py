#SN_CombinePathNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_CombinePathNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CombinePathNode"
    bl_label = "Combine Path"
    bl_icon = "PLUS"
    node_color = (0.125,0.125,0.125)
    should_be_registered = False

    docs = {
        "text": ["This node is used to <important>join two or more filepaths togethers</>.",
                ""],
        "python": ["os.path.join(<string>first_filepath</>, <string>second_filepath</>, <string>third_filepath</>)"]

    }

    def inititialize(self,context):
        self.sockets.create_input(self,"STRING","Path", dynamic=True)
        self.sockets.create_output(self,"STRING","Full Path")

    def evaluate(self, socket, node_data, errors):
        path = []
        for x, inp in enumerate(self.inputs):
            if inp.is_linked or inp.socket_value != "":
                path+=[node_data["input_data"][x]["code"], ", "]

        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["os.path.join("] + path + [")"]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }

    def required_imports(self):
        return ["os"]

