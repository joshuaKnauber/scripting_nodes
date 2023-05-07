import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_BreakNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_BreakNode"
    bl_label = "Break"
