import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_StringNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_StringNode"
    bl_label = "String"
