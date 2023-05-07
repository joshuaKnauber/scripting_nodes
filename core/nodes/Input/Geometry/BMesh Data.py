import bpy
from ...base_node import SN_BaseNode


class SN_BMeshDataNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_BMeshDataNode"
    bl_label = "BMesh Object Data"
