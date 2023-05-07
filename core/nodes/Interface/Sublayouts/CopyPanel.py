import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_CopyPanelNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_CopyPanelNodeNew"
    bl_label = "Copy Panel"
