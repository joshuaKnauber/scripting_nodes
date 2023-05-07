import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_OverrideContextNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_OverrideContextNode"
    bl_label = "Override Context"
