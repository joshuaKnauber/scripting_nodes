import bpy
from ...base_node import SN_BaseNode


class SN_ColorNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ColorNode"
    bl_label = "Color"
