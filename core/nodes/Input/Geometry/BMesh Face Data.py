import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_BMeshFaceDataNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_BMeshFaceDataNode"
    bl_label = "BMesh Face Data"
