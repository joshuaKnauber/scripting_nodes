import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_RunOperatorNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_RunOperatorNode"
    bl_label = "Run Operator"
