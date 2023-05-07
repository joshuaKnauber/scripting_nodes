import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_BooleanMathNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_BooleanMathNode"
    bl_label = "Boolean Math"
