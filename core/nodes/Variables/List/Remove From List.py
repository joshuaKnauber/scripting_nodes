import bpy
from ...base_node import SN_BaseNode


class SN_RemoveFromListNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RemoveFromListNode"
    bl_label = "Remove From List"
