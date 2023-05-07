import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_IsInListNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_IsInListNode"
    bl_label = "Element In List"
