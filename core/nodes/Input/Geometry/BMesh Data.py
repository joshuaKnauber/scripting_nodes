import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_BMeshDataNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_BMeshDataNode"
    bl_label = "BMesh Object Data"
