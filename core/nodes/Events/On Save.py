import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_OnSaveNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_OnSaveNode"
    bl_label = "On Save"
