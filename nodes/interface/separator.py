#SN_SeperatorNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_SeperatorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SeperatorNode"
    bl_label = "Seperator"
    bl_icon = "LINENUMBERS_OFF"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    docs = {
        "text": ["The separator node <important>separates the layout</>.",
                "",
                "Factor: <subtext>How big the separator is</>"],
        "python": ["layout.<function>separator</>(factor=<number>0.9</>)"]
    }

    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")
        factor = self.sockets.create_input(self, "FLOAT", "Factor")
        factor.set_value(1)

    def evaluate(self, socket, node_data, errors):
        layout_type = self.inputs[0].links[0].from_node.layout_type()
        
        return {
            "blocks": [
                {
                    "lines": [
                        [layout_type,".separator(factor=", node_data["input_data"][1]["code"], ")"],
                    ],
                    "indented": [
                    ]
                }
            ],
            "errors": errors
        }
