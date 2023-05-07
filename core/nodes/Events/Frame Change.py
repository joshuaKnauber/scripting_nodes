import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_ChangeFrameNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ChangeFrameNode"
    bl_label = "On Frame Change"
