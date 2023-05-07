import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_TextSizeNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_TextSizeNode"
    bl_label = "Text Size"
