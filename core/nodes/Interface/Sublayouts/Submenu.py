import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_SubmenuNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_SubmenuNodeNew"
    bl_label = "Submenu"
