import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_OpenPanelNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_OpenPanelNode"
    bl_label = "Open Panel"
