import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_SetModalCursorNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_SetModalCursorNode"
    bl_label = "Set Modal Cursor"
