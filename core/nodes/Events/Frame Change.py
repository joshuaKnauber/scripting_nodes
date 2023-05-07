import bpy
from ..base_node import SN_BaseNode


class SN_ChangeFrameNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ChangeFrameNode"
    bl_label = "On Frame Change"
