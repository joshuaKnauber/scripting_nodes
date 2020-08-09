#SN_ObjectContextNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_ObjectContextNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ObjectContextNode"
    bl_label = "Object Context"
    bl_icon = "WORLD"
    node_color = (0.53, 0.55, 0.53)
    should_be_registered = False

    def inititialize(self,context):
        self.sockets.create_output(self,"OBJECT", "Active bone")
        self.sockets.create_output(self,"OBJECT", "Active object")
        self.sockets.create_output(self,"OBJECT", "Active pose bone")
        self.sockets.create_output(self,"OBJECT", "Area")
        self.sockets.create_output(self,"OBJECT", "Collection")

        self.sockets.create_output(self,"STRING", "Engine")
        self.sockets.create_output(self,"STRING", "Mode")

        self.sockets.create_output(self,"OBJECT", "Pose object")
        self.sockets.create_output(self,"OBJECT", "Region")
        self.sockets.create_output(self,"OBJECT", "Scene")
        self.sockets.create_output(self,"OBJECT", "Screen")
        self.sockets.create_output(self,"OBJECT", "View layer")
        self.sockets.create_output(self,"OBJECT", "Window manager")
        self.sockets.create_output(self,"OBJECT", "Workspace")


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
