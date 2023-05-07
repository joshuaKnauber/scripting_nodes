import bpy
from ...base_node import SN_BaseNode


class SN_MeshBlendDataNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_MeshBlendDataNode"
    bl_label = "Meshes"
