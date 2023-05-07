import bpy
from ..base_node import SN_BaseNode


class SN_InModeNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_InModeNode"
    bl_label = "In Mode"
