import bpy
from ...base_node import SN_BaseNode


class SN_OpenMenuNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_OpenMenuNode"
    bl_label = "Open Menu"
