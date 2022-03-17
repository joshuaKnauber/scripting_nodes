import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_SceneContextNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SceneContextNode"
    bl_label = "Scene Context"
    node_color = "DEFAULT"

    def on_create(self, context):
        self.add_property_output("Active Scene")
        self.add_property_output("Active Area")
        self.add_property_output("Active View Layer")
        self.add_property_output("Active Camera")
        self.add_property_output("Active Bone")
        self.add_property_output("Active Pose Bone")
        self.add_property_output("Preferences")
        self.add_property_output("Window Manager")
        self.add_property_output("Window")
        self.add_property_output("Screen")
        self.add_string_output("Engine")
        self.add_string_output("Mode")
        self.add_string_output("Blend Filepath")
        self.add_boolean_output("File Is Saved")
        self.add_boolean_output("File Has Changes")
        self.add_integer_output("Current Frame")

    def evaluate(self, context):
        self.outputs["Active Scene"].python_value = f"bpy.context.scene"
        self.outputs["Active Area"].python_value = f"bpy.context.area"
        self.outputs["Active View Layer"].python_value = f"bpy.context.view_layer"
        self.outputs["Active Camera"].python_value = f"bpy.context.scene.camera"
        self.outputs["Active Bone"].python_value = f"bpy.context.active_bone"
        self.outputs["Active Pose Bone"].python_value = f"bpy.context.active_pose_bone"
        self.outputs["Preferences"].python_value = f"bpy.context.preferences"
        self.outputs["Window Manager"].python_value = f"bpy.context.window_manager"
        self.outputs["Window"].python_value = f"bpy.context.window"
        self.outputs["Screen"].python_value = f"bpy.context.screen"
        self.outputs["Engine"].python_value = f"bpy.context.engine"
        self.outputs["Mode"].python_value = f"bpy.context.mode"
        self.outputs["Blend Filepath"].python_value = f"bpy.data.filepath"
        self.outputs["File Is Saved"].python_value = f"bpy.data.is_saved"
        self.outputs["File Has Changes"].python_value = f"bpy.data.is_dirty"
        self.outputs["Current Frame"].python_value = f"bpy.context.scene.frame_current"