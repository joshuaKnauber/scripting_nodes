import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_SceneContextNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SceneContextNode"
    bl_label = "Scene Context"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def on_create(self,context):
        out = self.add_blend_data_output("Active Scene")
        out.data_type = "Scene"
        out.data_identifier = "scene"
        out = self.add_blend_data_output("Active Area")
        out.data_type = "Area"
        out.data_identifier = "area"
        out = self.add_blend_data_output("Active Camera")
        out.data_type = "Camera"
        out.data_identifier = "camera"
        out = self.add_blend_data_output("Preferences")
        out.data_type = "Preferences"
        out.data_identifier = "preferences"
        out = self.add_blend_data_output("Window Manager")
        out.data_type = "WindowManager"
        out.data_identifier = "window_manager"
        self.add_string_output("Engine")
        self.add_string_output("Mode")
        self.add_integer_output("Current Frame")
        self.add_boolean_output("File Is Saved")
        self.add_boolean_output("File Has Changes")
        self.add_string_output("Filepath")

    def code_evaluate(self, context, touched_socket):
        
        return_type = {
            "Active Scene": "bpy.context.scene",
            "Active Area": "bpy.context.area",
            "Active Camera": "bpy.context.scene.camera",
            "Preferences": "bpy.context.preferences",
            "Window Manager": "bpy.context.window_manager",
            "Engine": "bpy.context.engine",
            "Mode": "bpy.context.mode",
            "Current Frame": "bpy.context.scene.frame_current",
            "File Is Saved": "bpy.data.is_saved",
            "File Has Changes": "bpy.data.is_dirty",
            "Filepath": "bpy.data.filepath",
        }

        return {
            "code": f"{return_type[touched_socket.default_text]}"
        }