import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_IndexListNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_IndexListNode"
    bl_label = "Index List"
