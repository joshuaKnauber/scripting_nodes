import bpy
from ..base_node import SN_BaseNode


class SN_ButtonNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ButtonNodeNew"
    bl_label = "Button"
