import bpy
from ...base_node import SN_BaseNode


class SN_DrawTriangleNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_DrawTriangleNode"
    bl_label = "Draw Triangle"
