import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_DisplayPreviewNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_DisplayPreviewNodeNew"
    bl_label = "Display Preview"
