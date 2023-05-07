import bpy
from ...base_node import SN_BaseNode


class SN_BooleanVectorNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_BooleanVectorNode"
    bl_label = "Boolean Vector"
