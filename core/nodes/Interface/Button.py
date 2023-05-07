import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_ButtonNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ButtonNodeNew"
    bl_label = "Button"
