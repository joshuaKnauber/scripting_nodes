import bpy
from ...base_node import SN_BaseNode


class SN_IndexOfElementNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_IndexOfElementNode"
    bl_label = "Index Of List Element"
