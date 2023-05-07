import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_GetCustomPropertyNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_GetCustomPropertyNode"
    bl_label = "Get Custom Property"
