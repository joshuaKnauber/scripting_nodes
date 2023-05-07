import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_ScriptlineNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ScriptlineNode"
    bl_label = "Scriptline"
