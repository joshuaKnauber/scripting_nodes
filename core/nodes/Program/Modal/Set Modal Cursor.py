import bpy
from ...base_node import SN_BaseNode


class SN_SetModalCursorNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SetModalCursorNode"
    bl_label = "Set Modal Cursor"
