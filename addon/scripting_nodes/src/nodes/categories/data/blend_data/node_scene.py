import bpy

from .....sockets.spec import BlendData, Float, Integer, String
from ....base_node import ScriptingBaseNode

# output key -> expression
VALUES = {
    "scene": "bpy.context.scene",
    "camera": "bpy.context.scene.camera",
    "world": "bpy.context.scene.world",
    "view_layer": "bpy.context.view_layer",
    "collection": "bpy.context.scene.collection",
    "name": "bpy.context.scene.name",
    "frame_current": "bpy.context.scene.frame_current",
    "frame_start": "bpy.context.scene.frame_start",
    "frame_end": "bpy.context.scene.frame_end",
    "fps": "bpy.context.scene.render.fps",
}


class SNA_Node_Scene(ScriptingBaseNode, bpy.types.Node):
    """The current scene and some of its common properties."""

    bl_idname = "SNA_Node_Scene"
    bl_label = "Scene"
    sn_outputs = [
        BlendData("scene", "Scene"),
        BlendData("camera", "Camera"),
        BlendData("world", "World"),
        BlendData("view_layer", "View Layer"),
        BlendData("collection", "Collection"),
        String("name", "Name"),
        Integer("frame_current", "Frame Current"),
        Integer("frame_start", "Frame Start"),
        Integer("frame_end", "Frame End"),
        Float("fps", "FPS"),
    ]

    def emit(self, ctx):
        for key, expression in VALUES.items():
            ctx.output(key, expression)
