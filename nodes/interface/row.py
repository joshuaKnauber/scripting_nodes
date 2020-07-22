#SN_RowNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_RowNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RowNode"
    bl_label = "Row"
    bl_icon = "LINENUMBERS_OFF"
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
    
    def layout_type(self):
        return "row"
