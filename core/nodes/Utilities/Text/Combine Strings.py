import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_CombineStringsNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_CombineStringsNode"
    bl_label = "Combine Strings"
