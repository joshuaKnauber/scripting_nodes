import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_IfElseExecuteNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_IfElseExecuteNode"
    bl_label = "If/Else (Execute)"
