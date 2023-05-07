import bpy
from ...base_node import SN_BaseNode


class SN_CopyPanelNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_CopyPanelNodeNew"
    bl_label = "Copy Panel"
