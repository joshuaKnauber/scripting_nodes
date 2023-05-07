import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_SetAttributeNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_SetAttributeNode"
    bl_label = "Set Attribute"
