import bpy
from ...base_node import SN_BaseNode


class SN_RegionToViewNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RegionToViewNode"
    bl_label = "Region To View"
