import bpy
from ...base_node import SN_BaseNode


class SN_DrawModalTextNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_DrawModalTextNode"
    bl_label = "Draw Text"
