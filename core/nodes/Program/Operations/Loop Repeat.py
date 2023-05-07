import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_RepeatExecuteNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_RepeatExecuteNode"
    bl_label = "Loop Repeat (Execute)"
