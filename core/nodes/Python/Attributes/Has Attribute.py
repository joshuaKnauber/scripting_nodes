import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_HasAttributeNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_HasAttributeNode"
    bl_label = "Has Attribute"
