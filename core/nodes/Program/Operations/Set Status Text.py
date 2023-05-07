import bpy
from ...base_node import SN_BaseNode


class SN_SetStatusTextNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SetStatusTextNode"
    bl_label = "Set Status Text"
