import bpy
from ..base_node import SN_BaseNode


class SN_BeforeRenderNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_BeforeRenderNode"
    bl_label = "On Render Start"
