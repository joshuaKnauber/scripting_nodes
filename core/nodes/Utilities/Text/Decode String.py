import bpy
from ...base_node import SN_BaseNode


class SN_DecodeStringNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_DecodeStringNode"
    bl_label = "Decode Byte String"
