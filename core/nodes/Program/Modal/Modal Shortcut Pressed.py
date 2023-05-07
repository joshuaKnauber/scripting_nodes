import bpy
from ...base_node import SN_BaseNode


class SN_ModalShortcutPressedNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ModalShortcutPressedNode"
    bl_label = "Modal Shortcut Pressed"
