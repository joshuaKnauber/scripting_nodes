import bpy
from ...base_node import SN_BaseNode


class SN_RoundNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RoundNode"
    bl_label = "Round Number"
