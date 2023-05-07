import bpy
from ..base_node import SN_BaseNode


class SN_CompareNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_CompareNode"
    bl_label = "Compare"
