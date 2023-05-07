import bpy
from ...base_node import SN_BaseNode


class SN_StringLengthNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_StringLengthNode"
    bl_label = "String Length"
