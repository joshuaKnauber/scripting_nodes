import bpy
from ...base_node import SN_BaseNode


class SN_ModalViewportMovedNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ModalViewportMovedNode"
    bl_label = "Modal Viewport Moved"
