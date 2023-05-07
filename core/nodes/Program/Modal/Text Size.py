import bpy
from ...base_node import SN_BaseNode


class SN_TextSizeNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_TextSizeNode"
    bl_label = "Text Size"
