import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ListNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ListNode"
    bl_label = "List"
