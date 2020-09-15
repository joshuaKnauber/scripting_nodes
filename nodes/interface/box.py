#SN_BoxNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_BoxNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BoxNode"
    bl_label = "Box"
    bl_icon = "SNAP_FACE"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    docs = {
        "text": ["The box node can change a layout to be <important>displayed in a box</>.",
                "",
                "Enabled: <subtext>Only displays a box if this is True</>",
                "Alert: <subtext>Is diplayed red like an alert</>"],
        "python": ["layout.<function>box</>()"]
    }

    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")

        self.sockets.create_input(self,"BOOLEAN","Enabled").set_value(True)
        self.sockets.create_input(self,"BOOLEAN","Alert").set_value(False)

        self.sockets.create_input(self,"FLOAT","Scale X").set_value(1)
        self.sockets.create_input(self,"FLOAT","Scale Y").set_value(1)

        self.sockets.create_output(self,"LAYOUT","Layout", True)

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
                        ["box = ",layout_type,".box()"],
                        ["box.enabled = ", node_data["input_data"][1]["code"]],
                        ["box.alert = ", node_data["input_data"][2]["code"]],
                        ["box.scale_x = ", node_data["input_data"][3]["code"]],
                        ["box.scale_y = ", node_data["input_data"][4]["code"]]
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
        return "box"

