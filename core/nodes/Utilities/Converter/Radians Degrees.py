import bpy
from ...base_node import SN_BaseNode


class SN_RadiansNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RadiansNode"
    bl_label = "Convert Radians/Degrees"
