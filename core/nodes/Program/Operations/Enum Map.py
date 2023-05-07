import bpy
from ...base_node import SN_BaseNode


class SN_EnumMapNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_EnumMapNode"
    bl_label = "Enum Map (Execute)"
