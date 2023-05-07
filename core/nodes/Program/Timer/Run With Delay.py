import bpy
from ...base_node import SN_BaseNode


class SN_RunWithDelayNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RunWithDelayNode"
    bl_label = "Run With Delay"
