#SN_SetActiveObjectNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_SetActiveObjectNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SetActiveObjectNode"
    bl_label = "Set Active Object"
    bl_icon = "MESH_CUBE"
    node_color = (0.2, 0.2, 0.2)
    should_be_registered = False

    docs = {
        "text": ["The Set Active Object Node is used to <important>set an active Object</>.",
                "",
                "Object Input: <subtext>The object you want to set as active object</>"],
        "python": ["bpy.context.view_layer.objects.active = bpy.data.objects[0]"]

    }

    def reset_data_type(self, context):
        self.update_node()

    def inititialize(self,context):
        self.sockets.create_input(self,"EXECUTE","Execute")
        self.sockets.create_input(self,"OBJECT","Object")
        self.sockets.create_output(self,"EXECUTE","Execute")

    def update_node(self):
        if len(self.inputs[1].links):
            if self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket) != "bpy.types.Object":
                link = self.inputs[1].links[0]
                from_socket = link.from_socket
                to_socket = link.to_socket
                bpy.context.space_data.node_tree.links.remove(link)

    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if node_data["output_data"][0]["code"]:
            next_code = node_data["output_data"][0]["code"]

        active_object = "None"
        if node_data["input_data"][1]["code"]:
            active_object = node_data["input_data"][1]["code"]

        return {
            "blocks": [
                {
                    "lines": [
                        ["bpy.context.view_layer.objects.active = ", active_object]
                    ],
                    "indented": [
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

