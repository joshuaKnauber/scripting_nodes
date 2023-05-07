import bpy
from ...base_node import SN_BaseNode


class SN_RefreshViewNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RefreshViewNode"
    bl_label = "Refresh View"
