import bpy
from ..base_node import SN_BaseNode


class SN_SetVariableNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SetVariableNode"
    bl_label = "Set Variable"
