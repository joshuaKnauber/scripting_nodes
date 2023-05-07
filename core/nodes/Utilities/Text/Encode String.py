import bpy
from ...base_node import SN_BaseNode


class SN_EncodeStringNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_EncodeStringNode"
    bl_label = "Encode Byte String"
