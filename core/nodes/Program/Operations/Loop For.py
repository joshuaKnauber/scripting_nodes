import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ForExecuteNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ForExecuteNode"
    bl_label = "Loop For (Execute)"
