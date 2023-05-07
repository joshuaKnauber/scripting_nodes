import bpy
from ...base_node import SN_BaseNode


class SN_SplitVectorNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SplitVectorNode"
    bl_label = "Split Vector"
