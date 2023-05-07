import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_DefineDataType(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_DefineDataType"
    bl_label = "Define Data Type"
