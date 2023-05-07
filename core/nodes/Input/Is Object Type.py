import bpy
from ..base_node import SN_BaseNode


class SN_IsObjectType(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_IsObjectType"
    bl_label = "Is Object Type"
