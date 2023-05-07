import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_SortListNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_SortListNode"
    bl_label = "Sort List"
