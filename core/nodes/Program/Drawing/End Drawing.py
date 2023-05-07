import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_EndDrawingNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_EndDrawingNode"
    bl_label = "End Drawing"
