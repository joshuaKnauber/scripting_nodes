import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_DrawCircleNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_DrawCircleNode"
    bl_label = "Draw Circle"
