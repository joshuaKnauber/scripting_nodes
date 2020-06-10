import bpy
from ...node_sockets import update_socket_autocompile
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from .scene_nodes_utils import add_data_output, get_active_types, get_bpy_types


class SN_ContextDataNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Context Node for outputing context data'''
    bl_idname = 'SN_ContextDataNode'
    bl_label = "Context"
    bl_icon = node_icons["SCENE"]


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


    def copy(self, node):
        pass

    def free(self):
        pass

    def draw_buttons(self, context, layout):
        pass

    def evaluate(self, output):
        code = []

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
        code += ["bpy.context.", context_type]

        return {"code": code}

    def internal_evaluate(self, output):
        if output.bl_idname == "SN_SceneDataSocket":
            code = []
            
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
            code += ["bpy.types.", context_type]

            return {"code": code}
        else:
            return {"code": [""]}

