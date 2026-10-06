from ....base_node import ScriptingBaseNode
import bpy


class SNA_Node_Scene(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Scene"
    bl_label = "Scene"

    def on_create(self):
        self.add_output("ScriptingBlendDataSocket", "Scene")
        self.add_output("ScriptingBlendDataSocket", "Camera")
        self.add_output("ScriptingBlendDataSocket", "World")
        self.add_output("ScriptingBlendDataSocket", "View Layer")
        self.add_output("ScriptingBlendDataSocket", "Collection")
        self.add_output("ScriptingStringSocket", "Name")
        self.add_output("ScriptingIntegerSocket", "Frame Current")
        self.add_output("ScriptingIntegerSocket", "Frame Start")
        self.add_output("ScriptingIntegerSocket", "Frame End")
        self.add_output("ScriptingFloatSocket", "FPS")

    def generate(self):
        self.outputs["Scene"].code = "bpy.context.scene"
        self.outputs["Camera"].code = "bpy.context.scene.camera"
        self.outputs["World"].code = "bpy.context.scene.world"
        self.outputs["View Layer"].code = "bpy.context.view_layer"
        self.outputs["Collection"].code = "bpy.context.scene.collection"
        self.outputs["Name"].code = "bpy.context.scene.name"
        self.outputs["Frame Current"].code = "bpy.context.scene.frame_current"
        self.outputs["Frame Start"].code = "bpy.context.scene.frame_start"
        self.outputs["Frame End"].code = "bpy.context.scene.frame_end"
        self.outputs["FPS"].code = "bpy.context.scene.render.fps"
