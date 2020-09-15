#SN_SplitNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_SplitNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SplitNode"
    bl_label = "Split"
    bl_icon = "UV_ISLANDSEL"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    docs = {
        "text": ["The split node can change a layout to <important>be split in two sides</>.",
                "",
                "Aligned: <subtext>Align all layouts with each other</>",
                "Enabled: <subtext>Only splits the layout if this is True</>",
                "Alert: <subtext>Is diplayed red like an alert</>"],
        "python": ["layout.<function>split</>(align=<red>True</>, factor=<number>0.4</>)"]
    }

    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")
        factor = self.sockets.create_input(self, "FLOAT", "Factor")
        factor.set_value(0.5)
        factor.use_factor = True

        self.sockets.create_input(self,"BOOLEAN","Aligned").set_value(False)
        self.sockets.create_input(self,"BOOLEAN","Enabled").set_value(True)
        self.sockets.create_input(self,"BOOLEAN","Alert").set_value(False)

        self.sockets.create_input(self,"FLOAT","Scale X").set_value(1)
        self.sockets.create_input(self,"FLOAT","Scale Y").set_value(1)

        self.sockets.create_output(self,"LAYOUT","Layout")
        self.sockets.create_output(self,"LAYOUT","Layout")

    def evaluate(self, socket, node_data, errors):
        layout_type = self.inputs[0].links[0].from_node.layout_type()
        
        next_layout = []
        for output_data in node_data["output_data"]:
            if output_data["code"] != None:
                next_layout.append([output_data["code"]])

        return {
            "blocks": [
                {
                    "lines": [
                        ["split = ",layout_type,".split(align=", node_data["input_data"][2]["code"], ", factor=", node_data["input_data"][1]["code"], ")"],
                        ["split.enabled = ", node_data["input_data"][3]["code"]],
                        ["split.alert = ", node_data["input_data"][4]["code"]],
                        ["split.scale_x = ", node_data["input_data"][5]["code"]],
                        ["split.scale_y = ", node_data["input_data"][6]["code"]]
                    ],
                    "indented": [
                    ]
                },
                {
                    "lines": next_layout,
                    "indented": []
                }
            ],
            "errors": errors
        }

    def layout_type(self):
        return "split"