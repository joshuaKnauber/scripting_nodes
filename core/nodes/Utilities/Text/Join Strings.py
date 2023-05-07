import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_JoinStringsNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_JoinStringsNode"
    bl_label = "Join Strings"
