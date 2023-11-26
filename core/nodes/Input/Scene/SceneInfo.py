import bpy

from .....constants import sockets
from ...base_node import SNA_BaseNode


class SNA_NodeSceneInfo(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeSceneInfo"
    bl_label = "Scene Info"

    def on_create(self):
        self.add_output(sockets.PROPERTY, "Active Scene")
        self.add_output(sockets.PROPERTY, "Active Object")
        self.add_output(sockets.PROPERTY, "Active Camera")

    def generate(self, context, trigger):
        self.outputs["Active Scene"].code = f"bpy.context.scene"
        self.outputs["Active Scene"].set_meta("type", "Scene")
        self.outputs["Active Scene"].set_meta("parent", "bpy.context")
        self.outputs["Active Scene"].set_meta("identifier", "scene")

        self.outputs["Active Object"].code = f"bpy.context.object"
        self.outputs["Active Object"].set_meta("type", "Object")
        self.outputs["Active Object"].set_meta("parent", "bpy.context")
        self.outputs["Active Object"].set_meta("identifier", "object")

        self.outputs["Active Camera"].code = f"bpy.context.scene.camera"
        self.outputs["Active Camera"].set_meta("type", "Camera")
        self.outputs["Active Camera"].set_meta("parent", "bpy.context.scene")
        self.outputs["Active Camera"].set_meta("identifier", "camera")
