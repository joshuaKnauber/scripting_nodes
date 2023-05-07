import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_SeparatorNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_SeparatorNodeNew"
    bl_label = "Separator"
