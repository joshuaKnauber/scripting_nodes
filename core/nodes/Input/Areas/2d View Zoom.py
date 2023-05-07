import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_2DViewZoomNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_2DViewZoomNode"
    bl_label = "2D View Zoom"
