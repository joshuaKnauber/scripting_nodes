#SN_ForLayoutNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_ForLayoutNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ForLayoutNode"
    bl_label = "For (Layout)"
    bl_icon = "CON_ACTION"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    def reset_data_type(self, context):
        if self.inputs[1].links[0].from_socket.bl_idname in ["SN_CollectionSocket", "SN_ObjectSocket"]:
            if self.outputs[1].is_linked:
                if self.outputs[1].links[0].to_socket.bl_idname in ["SN_CollectionSocket", "SN_ObjectSocket"]:
                    self.outputs[1].links[0].to_node.reset_data_type(None)
            else:
                self.update()

    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")
        self.sockets.create_input(self,"COLLECTION","Input")
        self.sockets.create_output(self,"LAYOUT","Repeat")
        self.sockets.create_output(self,"OBJECT","Element")
        self.sockets.create_output(self,"INTEGER","Index")

    def draw_buttons(self, context, layout):
        if len(self.inputs[1].links) == 1:
            if self.inputs[1].links[0].from_socket.bl_idname == "SN_CollectionSocket":
                data_type = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)
                if data_type != "":
                    box = layout.box()
                    box.label(text=eval(data_type).bl_rna.name)

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

    def data_type(self, output):
        if len(self.inputs[1].links) == 1:
            if self.inputs[1].links[0].from_socket.bl_idname == "SN_CollectionSocket":
                data_type = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)
                if data_type != "":
                    return data_type

        return ""

