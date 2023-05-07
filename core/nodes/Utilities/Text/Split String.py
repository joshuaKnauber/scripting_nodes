import bpy
from ...base_node import SN_BaseNode


class SN_SplitStringNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SplitStringNode"
    bl_label = "Split String"
