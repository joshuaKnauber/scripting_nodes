import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_ChangeVariableByNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ChangeVariableByNode"
    bl_label = "Change Variable By"
