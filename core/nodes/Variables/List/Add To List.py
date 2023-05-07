import bpy
from ...base_node import SN_BaseNode


class SN_AddToListNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_AddToListNode"
    bl_label = "Add To List"
