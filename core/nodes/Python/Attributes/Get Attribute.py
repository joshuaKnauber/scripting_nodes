import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_GetAttributeNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_GetAttributeNode"
    bl_label = "Get Attribute"
