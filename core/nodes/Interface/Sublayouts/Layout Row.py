import bpy
from ...base_node import SN_BaseNode


class SN_LayoutRowNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_LayoutRowNodeNew"
    bl_label = "Row"
