import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_IsInStringNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_IsInStringNode"
    bl_label = "Substring is in String"
