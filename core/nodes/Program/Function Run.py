import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_RunFunctionNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_RunFunctionNode"
    bl_label = "Function Run (Execute)"
