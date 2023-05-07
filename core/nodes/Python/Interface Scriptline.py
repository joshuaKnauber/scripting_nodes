import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_InterfaceScriptlineNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_InterfaceScriptlineNode"
    bl_label = "Interface Scriptline"
