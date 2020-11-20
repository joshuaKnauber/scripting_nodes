#SN_ObjectContextNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_ObjectContextNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ObjectContextNode"
    bl_label = "Object Context"
    bl_icon = "WORLD"
    node_color = (0.53, 0.55, 0.53)
    should_be_registered = False

    docs = {
        "text": ["This node has a few outputs for <important>important objects</>.",
                "Tip: Press CTRL + H to hide unnecessary outputs",
                ""],
        "python": ["bpy.context.active_object"]

    }

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
        self.sockets.create_output(self,"OBJECT", "Preferences")


    def evaluate(self, socket, node_data, errors):
        context_type = {
            "Active bone": "active_bone",
            "Active object": "active_object",
            "Active pose bone": "active_pose_bone",
            "Area": "area",
            "Collection": "collection",
            "Engine": "engine",
            "Mode": "mode",
            "Pose Object": "pose_object",
            "Region": "region",
            "Scene": "scene",
            "Screen": "screen",
            "View layer": "view_layer",
            "Window manager": "window_manager",
            "Workspace": "workspace",
            "Preferences": "preferences",
        }
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                        ["bpy.context." + context_type[socket.name]]
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": errors
        }


    def data_type(self, output):
        context_type = {
            "Active bone": "Bone",
            "Active object": "Object",
            "Active pose bone": "PoseBone",
            "Area": "Area",
            "Collection": "Collection",
            "Pose Object": "Object",
            "Region": "Region",
            "Scene": "Scene",
            "Screen": "Screen",
            "View layer": "ViewLayer",
            "Window manager": "WindowManager",
            "Workspace": "WorkSpace",
            "Preferences": "Preferences",
        }

        context_type = context_type[output.name]

        return "bpy.types." + context_type
