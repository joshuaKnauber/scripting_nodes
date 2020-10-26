#SN_BetterLabelNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_BetterLabelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BetterLabelNode"
    bl_label = "Better Label"
    bl_icon = "SORTALPHA"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    docs = {
        "text": ["The label node can add <important>text and an icon</> in your interface.",
                "",
                "Text: <subtext>The text that will be shown on the label</>"],
        "python": ["layout.<function>label</>(text=<string>\"My label text\"</>, icon=<string>\"MONKEY\"</>)"]
    }

    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")
        self.sockets.create_input(self,"STRING","Text",True)

    def draw_buttons(self,context,layout):
        self.draw_icon_chooser(layout)

    def evaluate(self, socket, node_data, errors):
        # get layout type
        layout_type = self.inputs[0].links[0].from_node.layout_type()

        # get label text
        label_text = []
        for i in range(1, len(self.inputs)):
            label_text.append(node_data["input_data"][i]["code"])
        if not label_text:
            label_text = ["\"\""]
        
        # get icon
        icon = self.icon
        if icon:
            icon = f", icon=\"{icon}\""

        return {
            "blocks": [
                {
                    "lines": [
                        [layout_type,".label(text="] + label_text + [icon,")"]
                    ],
                    "indented": []
                }
            ],
            "errors": errors
        }
