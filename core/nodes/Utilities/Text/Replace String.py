import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ReplaceStringNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ReplaceStringNode"
    bl_label = "Replace in String"
