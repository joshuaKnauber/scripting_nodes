import bpy
from ..base_node import SN_BaseNode


class SN_SleepNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SleepNode"
    bl_label = "Sleep"
    bl_width_default = 200
