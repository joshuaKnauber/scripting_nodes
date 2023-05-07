import bpy
from ...base_node import SN_BaseNode


class SN_2DViewZoomNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_2DViewZoomNode"
    bl_label = "2D View Zoom"
