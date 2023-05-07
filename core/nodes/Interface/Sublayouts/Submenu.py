import bpy
from ...base_node import SN_BaseNode


class SN_SubmenuNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SubmenuNodeNew"
    bl_label = "Submenu"
