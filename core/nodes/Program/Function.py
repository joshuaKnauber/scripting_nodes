import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_FunctionNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_FunctionNode"
    bl_label = "Function (Execute)"
