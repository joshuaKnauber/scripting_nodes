import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_CopyMenuNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_CopyMenuNodeNew"
    bl_label = "Copy Menu"
