import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_SetPropertyNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_SetPropertyNode"
    bl_label = "Set Property"
