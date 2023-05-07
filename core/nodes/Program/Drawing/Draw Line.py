import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_DrawLineNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_DrawLineNode"
    bl_label = "Draw Line"
