import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_ContextDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ContextDataNode"
    bl_label = "Context Data"
    bl_icon = node_icons["SCENE"]
    _should_be_registered = False

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def generate_sockets(self):
        out = self.outputs.new("SN_SceneDataSocket", "Active bone")
        out.display_shape = "SQUARE"
        out = self.outputs.new("SN_SceneDataSocket", "Active object")
        out.display_shape = "SQUARE"
        out = self.outputs.new("SN_SceneDataSocket", "Active pose bone")
        out.display_shape = "SQUARE"
        out = self.outputs.new("SN_SceneDataSocket", "Area")
        out.display_shape = "SQUARE"
        out = self.outputs.new("SN_SceneDataSocket", "Collection")
        out.display_shape = "SQUARE"

        self.outputs.new("SN_StringSocket", "Engine")
        self.outputs.new("SN_StringSocket", "Mode")

        out = self.outputs.new("SN_SceneDataSocket", "Pose object")
        out.display_shape = "SQUARE"
        out = self.outputs.new("SN_SceneDataSocket", "Region")
        out.display_shape = "SQUARE"
        out = self.outputs.new("SN_SceneDataSocket", "Scene")
        out.display_shape = "SQUARE"
        out = self.outputs.new("SN_SceneDataSocket", "Screen")
        out.display_shape = "SQUARE"
        out = self.outputs.new("SN_SceneDataSocket", "View layer")
        out.display_shape = "SQUARE"
        out = self.outputs.new("SN_SceneDataSocket", "Window manager")
        out.display_shape = "SQUARE"
        out = self.outputs.new("SN_SceneDataSocket", "Workspace")
        out.display_shape = "SQUARE"

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INPUT"]

        self.generate_sockets()


    def evaluate(self, output):
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
        }

        context_type = context_type[output.name]
        
        return {
            "blocks": [
                {
                    "lines": [
                        ["bpy.context." + context_type]
                    ],
                    "indented": [
                        
                    ]
                }
            ],
            "errors": []
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
            "View layer": "View_Layer",
            "Window manager": "Window_Manager",
            "Workspace": "WorkSpace",
        }

        context_type = context_type[output.name]

        return "bpy.types." + context_type

    def needed_imports(self):
        return []