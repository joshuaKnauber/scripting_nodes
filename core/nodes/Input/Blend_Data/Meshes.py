import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_MeshBlendDataNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_MeshBlendDataNode"
    bl_label = "Meshes"
