import bpy
from ...base_node import SN_BaseNode


class SN_ListLengthNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ListLengthNode"
    bl_label = "List Length"
