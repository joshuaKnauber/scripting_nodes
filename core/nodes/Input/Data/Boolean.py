import bpy
from ...base_node import SN_BaseNode


class SN_BooleanNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_BooleanNode"
    bl_label = "Boolean"
