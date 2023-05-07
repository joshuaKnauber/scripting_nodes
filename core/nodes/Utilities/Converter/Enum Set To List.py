import bpy
from ...base_node import SN_BaseNode


class SN_EnumSetToListNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_EnumSetToListNode"
    bl_label = "Enum Set To List"
