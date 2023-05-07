import bpy
from ...base_node import SN_BaseNode


class SN_ListNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ListNode"
    bl_label = "List"
