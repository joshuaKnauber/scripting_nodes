import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_PanelNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_PanelNode"
    bl_label = "Panel"
