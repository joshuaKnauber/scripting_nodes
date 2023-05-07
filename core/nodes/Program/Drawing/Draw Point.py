import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_DrawPointNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_DrawPointNode"
    bl_label = "Draw Point"
