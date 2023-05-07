import bpy
from ..base_node import SN_BaseNode


class SN_OnPropertyUpdateNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_OnPropertyUpdateNode"
    bl_label = "On Property Update"
