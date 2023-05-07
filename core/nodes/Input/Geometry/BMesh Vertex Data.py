import bpy
from ...base_node import SN_BaseNode


class SN_BMeshVertexDataNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_BMeshVertexDataNode"
    bl_label = "BMesh Vertex Data"
