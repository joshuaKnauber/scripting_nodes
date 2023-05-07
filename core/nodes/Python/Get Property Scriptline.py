import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_GetPropertyScriptlineNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_GetPropertyScriptlineNode"
    bl_label = "Get Property Scriptline"
