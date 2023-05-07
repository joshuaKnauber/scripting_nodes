import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_AddToMenuNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_AddToMenuNodeNew"
    bl_label = "Add To Menu"
