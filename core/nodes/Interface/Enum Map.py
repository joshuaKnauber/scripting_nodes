import bpy
from ..base_node import SN_BaseNode


class SN_EnumMapInterfaceNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_EnumMapInterfaceNode"
    bl_label = "Enum Map (Interface)"
