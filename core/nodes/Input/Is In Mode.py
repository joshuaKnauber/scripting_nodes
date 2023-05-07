import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_InModeNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_InModeNode"
    bl_label = "In Mode"
