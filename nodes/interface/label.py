#SN_LabelNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_LabelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_LabelNode"
    bl_label = "Label"
    bl_icon = "SORTALPHA"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")
        self.sockets.create_input(self,"STRING","Text")

    def draw_buttons(self,context,layout):
        self.draw_icon_chooser(layout)

    def evaluate(self, socket, node_data, errors):
        layout_type = self.inputs[0].links[0].from_node.layout_type()
        icon = self.icon
        if icon:
            icon = f", icon=\"{icon}\""
        return {
            "blocks": [
                {
                    "lines": [
                        [layout_type,".label(text=",node_data["input_data"][1]["code"],icon,")"]
                    ],
                    "indented": []
                }
            ],
            "errors": errors
        }
