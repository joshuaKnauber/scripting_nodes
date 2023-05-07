import bpy
from ..base_node import SN_BaseNode


class SN_TimeNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_TimeNode"
    bl_label = "Time and Date"
