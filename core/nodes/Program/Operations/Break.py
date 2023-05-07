import bpy
from ...base_node import SN_BaseNode


class SN_BreakNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_BreakNode"
    bl_label = "Break"
