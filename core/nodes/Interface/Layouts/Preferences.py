import bpy
from ...base_node import SN_BaseNode


class SN_PreferencesNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_PreferencesNode"
    bl_label = "Preferences"
