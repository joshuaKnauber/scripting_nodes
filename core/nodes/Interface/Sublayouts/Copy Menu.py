import bpy
from ...base_node import SN_BaseNode


class SN_CopyMenuNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_CopyMenuNodeNew"
    bl_label = "Copy Menu"
