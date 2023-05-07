import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ModalShortcutPressedNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ModalShortcutPressedNode"
    bl_label = "Modal Shortcut Pressed"
