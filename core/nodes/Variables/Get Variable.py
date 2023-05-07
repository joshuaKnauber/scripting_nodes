import bpy
from ..base_node import SN_BaseNode


class SN_GetVariableNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_GetVariableNode"
    bl_label = "Get Variable"
