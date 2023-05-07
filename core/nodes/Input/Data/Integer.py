import bpy
from ...base_node import SN_BaseNode


class SN_IntegerNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_IntegerNode"
    bl_label = "Integer"
