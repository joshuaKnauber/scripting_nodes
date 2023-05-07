import bpy
from ...base_node import SN_BaseNode


class SN_AbsolutePathNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_AbsolutePathNode"
    bl_label = "Make Path Absolute"
