import bpy
from ..base_node import SN_BaseNode


class SN_ToggleVariableNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ToggleVariableNode"
    bl_label = "Toggle Variable"
