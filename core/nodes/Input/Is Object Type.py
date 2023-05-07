import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_IsObjectType(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_IsObjectType"
    bl_label = "Is Object Type"
