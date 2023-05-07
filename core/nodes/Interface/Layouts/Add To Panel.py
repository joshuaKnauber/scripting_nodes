import bpy
from ...base_node import SN_BaseNode


class SN_AddToPanelNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_AddToPanelNodeNew"
    bl_label = "Add To Panel"
