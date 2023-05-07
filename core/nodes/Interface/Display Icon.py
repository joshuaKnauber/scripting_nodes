import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_DisplayIconNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_DisplayIconNodeNew"
    bl_label = "Display Icon"
