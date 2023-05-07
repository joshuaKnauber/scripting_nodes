import bpy
from ...base_node import SN_BaseNode


class SN_OverrideContextNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_OverrideContextNode"
    bl_label = "Override Context"
