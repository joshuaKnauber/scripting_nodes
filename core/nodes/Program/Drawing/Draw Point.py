import bpy
from ...base_node import SN_BaseNode


class SN_DrawPointNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_DrawPointNode"
    bl_label = "Draw Point"
