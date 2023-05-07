import bpy
from ...base_node import SN_BaseNode


class SN_SetHeaderTextNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SetHeaderTextNode"
    bl_label = "Set Header Text"
