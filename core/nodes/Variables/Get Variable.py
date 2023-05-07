import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_GetVariableNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_GetVariableNode"
    bl_label = "Get Variable"
