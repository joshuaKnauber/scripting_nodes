import bpy
from ...base_node import SN_BaseNode


class SN_BMeshFaceDataNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_BMeshFaceDataNode"
    bl_label = "BMesh Face Data"
