import bpy
from ...base_node import SN_BaseNode


class SN_JoinStringsNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_JoinStringsNode"
    bl_label = "Join Strings"
