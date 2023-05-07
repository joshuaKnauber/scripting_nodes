import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_ResetVariableNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ResetVariableNode"
    bl_label = "Reset Variable"
