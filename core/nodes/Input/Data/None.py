import bpy
from ...base_node import SN_BaseNode


class SN_NoneNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_NoneNode"
    bl_label = "None"
