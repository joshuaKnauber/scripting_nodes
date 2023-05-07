import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_SetCustomPropertyNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_SetCustomPropertyNode"
    bl_label = "Set Custom Property"
