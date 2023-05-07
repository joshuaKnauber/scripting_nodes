import bpy
from ...base_node import SN_BaseNode


class SN_BMeshEdgeDataNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_BMeshEdgeDataNode"
    bl_label = "BMesh Edge Data"
