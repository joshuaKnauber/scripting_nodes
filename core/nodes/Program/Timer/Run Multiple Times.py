import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_RunMultipleTimesNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_RunMultipleTimesNode"
    bl_label = "Run Multiple Times"
