import bpy
from ..base_node import SN_BaseNode


class SN_DisplaySearchNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_DisplaySearchNodeNew"
    bl_label = "Display Search"
