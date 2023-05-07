import bpy
from ..base_node import SN_BaseNode


class SN_DisplayPropertyNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_DisplayPropertyNodeNew"
    bl_label = "Display Property"
