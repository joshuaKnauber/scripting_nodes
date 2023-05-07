import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_GetEditSelectNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_GetEditSelectNode"
    bl_label = "Get Edit Select Mode"
