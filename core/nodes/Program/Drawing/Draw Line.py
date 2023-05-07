import bpy
from ...base_node import SN_BaseNode


class SN_DrawLineNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_DrawLineNode"
    bl_label = "Draw Line"
