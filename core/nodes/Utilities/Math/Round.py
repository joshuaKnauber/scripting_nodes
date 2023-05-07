import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_RoundNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_RoundNode"
    bl_label = "Round Number"
