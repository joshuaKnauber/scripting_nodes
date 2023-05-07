import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_OpenMenuNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_OpenMenuNode"
    bl_label = "Open Menu"
