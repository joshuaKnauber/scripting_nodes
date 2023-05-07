import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ObjectToBMeshNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ObjectToBMeshNode"
    bl_label = "Object To BMesh"
