import bpy
from ...base_node import SN_BaseNode


class SN_BooleanMathNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_BooleanMathNode"
    bl_label = "Boolean Math"
