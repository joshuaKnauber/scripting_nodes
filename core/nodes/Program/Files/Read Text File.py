import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ReadTextFileNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ReadTextFileNode"
    bl_label = "Read Text File"
