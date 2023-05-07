import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_ToggleVariableNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ToggleVariableNode"
    bl_label = "Toggle Variable"
