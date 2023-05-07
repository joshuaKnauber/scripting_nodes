import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_BMeshEdgeDataNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_BMeshEdgeDataNode"
    bl_label = "BMesh Edge Data"
