import bpy
from ...base_node import SN_BaseNode


class SN_PieMenuNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_PieMenuNode"
    bl_label = "Pie Menu"
