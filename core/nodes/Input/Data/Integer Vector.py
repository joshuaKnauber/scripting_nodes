import bpy
from ...base_node import SN_BaseNode


class SN_IntegerVectorNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_IntegerVectorNode"
    bl_label = "Integer Vector"
