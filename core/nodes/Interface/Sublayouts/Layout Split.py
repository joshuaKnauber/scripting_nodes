import bpy
from ...base_node import SN_BaseNode


class SN_LayoutSplitNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_LayoutSplitNodeNew"
    bl_label = "Split"
