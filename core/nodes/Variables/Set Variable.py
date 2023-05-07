import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_SetVariableNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_SetVariableNode"
    bl_label = "Set Variable"
