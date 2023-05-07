import bpy
from ...base_node import SN_BaseNode


class SN_RunInIntervalsNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RunInIntervalsNode"
    bl_label = "Run In Intervals"
