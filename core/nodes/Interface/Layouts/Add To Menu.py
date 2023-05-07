import bpy
from ...base_node import SN_BaseNode


class SN_AddToMenuNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_AddToMenuNodeNew"
    bl_label = "Add To Menu"
