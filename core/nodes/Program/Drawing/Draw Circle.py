import bpy
from ...base_node import SN_BaseNode


class SN_DrawCircleNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_DrawCircleNode"
    bl_label = "Draw Circle"
