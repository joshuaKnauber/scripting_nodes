import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_OnPropertyUpdateNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_OnPropertyUpdateNode"
    bl_label = "On Property Update"
