import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ListLengthNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ListLengthNode"
    bl_label = "List Length"
