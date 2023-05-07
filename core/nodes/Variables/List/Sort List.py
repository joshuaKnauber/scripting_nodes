import bpy
from ...base_node import SN_BaseNode


class SN_SortListNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SortListNode"
    bl_label = "Sort List"
