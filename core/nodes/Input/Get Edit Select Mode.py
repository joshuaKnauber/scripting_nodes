import bpy
from ..base_node import SN_BaseNode


class SN_GetEditSelectNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_GetEditSelectNode"
    bl_label = "Get Edit Select Mode"
