import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ModalViewportMovedNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ModalViewportMovedNode"
    bl_label = "Modal Viewport Moved"
