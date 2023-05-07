import bpy
from ..base_node import SN_BaseNode


class SN_RandomNumberNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RandomNumberNode"
    bl_label = "Random Number"
