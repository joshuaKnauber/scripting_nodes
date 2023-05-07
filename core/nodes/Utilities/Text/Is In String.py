import bpy
from ...base_node import SN_BaseNode


class SN_IsInStringNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_IsInStringNode"
    bl_label = "Substring is in String"
