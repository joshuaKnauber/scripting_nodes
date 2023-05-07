import bpy
from ...base_node import SN_BaseNode


class SN_ViewToRegionNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ViewToRegionNode"
    bl_label = "View To Region"
