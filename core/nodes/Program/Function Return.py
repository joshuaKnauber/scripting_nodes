import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_FunctionReturnNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_FunctionReturnNode"
    bl_label = "Function Return (Execute)"
