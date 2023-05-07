import bpy
from ..base_node import SN_BaseNode


class SN_RandomColorNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RandomColorNode"
    bl_label = "Random Color"
