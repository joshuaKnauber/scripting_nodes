import bpy
from ...base_node import SN_BaseNode


class SN_LayoutColumnNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_LayoutColumnNodeNew"
    bl_label = "Column"
