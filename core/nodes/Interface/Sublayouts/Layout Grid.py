import bpy
from ...base_node import SN_BaseNode


class SN_LayoutGridNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_LayoutGridNode"
    bl_label = "Grid"
