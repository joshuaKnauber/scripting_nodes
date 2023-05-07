import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_RemoveFromListNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_RemoveFromListNode"
    bl_label = "Remove From List"
