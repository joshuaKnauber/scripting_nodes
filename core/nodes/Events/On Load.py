import bpy
from ..base_node import SN_BaseNode


class SN_OnLoadNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_OnLoadNode"
    bl_label = "On Load"
