import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_GetDataScriptlineNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_GetDataScriptlineNode"
    bl_label = "Get Data Scriptline"
