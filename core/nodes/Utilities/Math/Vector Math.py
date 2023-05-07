import bpy
from ...base_node import SN_BaseNode


class SN_VectorMathNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_VectorMathNode"
    bl_label = "Vector Math"
