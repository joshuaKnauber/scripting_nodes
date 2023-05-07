import bpy
from ...base_node import SN_BaseNode


class SN_OpenPieMenuNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_OpenPieMenuNode"
    bl_label = "Open Pie Menu"
