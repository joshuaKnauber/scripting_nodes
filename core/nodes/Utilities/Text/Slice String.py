import bpy
from ...base_node import SN_BaseNode


class SN_SliceStringNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SliceStringNode"
    bl_label = "Slice String"
