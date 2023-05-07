import bpy
from ...base_node import SN_BaseNode


class SN_ObjectToBMeshNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ObjectToBMeshNode"
    bl_label = "Object To BMesh"
