import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_DrawModalTextNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_DrawModalTextNode"
    bl_label = "Draw Text"
