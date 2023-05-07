import bpy
from ..base_node import SN_BaseNode


class SN_AfterRenderNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_AfterRenderNode"
    bl_label = "On Render Finish"
