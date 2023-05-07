import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_DisplaySerpensShortcutNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_DisplaySerpensShortcutNodeNew"
    bl_label = "Display Serpens Shortcut"
