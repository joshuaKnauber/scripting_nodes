import bpy
from ..base_node import SN_BaseNode


class SN_OnKeypressNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_OnKeypressNode"
    bl_label = "On Keypress"
