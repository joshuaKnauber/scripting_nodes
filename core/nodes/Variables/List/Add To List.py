import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_AddToListNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_AddToListNode"
    bl_label = "Add To List"
