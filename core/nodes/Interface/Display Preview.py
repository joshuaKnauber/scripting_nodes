import bpy
from ..base_node import SN_BaseNode


class SN_DisplayPreviewNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_DisplayPreviewNodeNew"
    bl_label = "Display Preview"
