#SN_ColumnNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_ColumnNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ColumnNode"
    bl_label = "Column"
    bl_icon = "RIGHTARROW"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")

        self.sockets.create_input(self,"BOOLEAN","Aligned").set_value(False)
        self.sockets.create_input(self,"BOOLEAN","Enabled").set_value(True)
        self.sockets.create_input(self,"BOOLEAN","Alert").set_value(False)

        self.sockets.create_input(self,"FLOAT","Scale X").set_value(1)
        self.sockets.create_input(self,"FLOAT","Scale X").set_value(1)

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
                        ["column = ",layout_type,".column(align=", node_data["input_data"][1]["code"], ")"],
                        ["column.enabled = ", node_data["input_data"][2]["code"]],
                        ["column.alert = ", node_data["input_data"][3]["code"]],
                        ["column.scale_x = ", node_data["input_data"][4]["code"]],
                        ["column.scale_y = ", node_data["input_data"][5]["code"]]
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
        return "column"
