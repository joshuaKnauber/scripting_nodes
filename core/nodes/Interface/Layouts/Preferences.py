import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_PreferencesNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_PreferencesNode"
    bl_label = "Preferences"
