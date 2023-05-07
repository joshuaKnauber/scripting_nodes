import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_SetEditSelectNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_SetEditSelectNode"
    bl_label = "Set Edit Select"
