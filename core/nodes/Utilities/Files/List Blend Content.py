import bpy
from ...base_node import SN_BaseNode


class SN_ListBlendContentNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ListBlendContentNode"
    bl_label = "List Blend File Content"
