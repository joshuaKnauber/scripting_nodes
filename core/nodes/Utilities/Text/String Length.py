import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_StringLengthNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_StringLengthNode"
    bl_label = "String Length"
