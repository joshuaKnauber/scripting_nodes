import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_DisplayPropertyNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_DisplayPropertyNodeNew"
    bl_label = "Display Property"
