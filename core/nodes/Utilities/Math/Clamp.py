import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ClampNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ClampNode"
    bl_label = "Clamp"
