import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_SetStatusTextNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_SetStatusTextNode"
    bl_label = "Set Status Text"
