import bpy
from ...base_node import SN_BaseNode


class SN_IsInListNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_IsInListNode"
    bl_label = "Element In List"
