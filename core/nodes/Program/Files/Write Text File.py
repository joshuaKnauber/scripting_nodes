import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_WriteTextFileNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_WriteTextFileNode"
    bl_label = "Write Text File"
