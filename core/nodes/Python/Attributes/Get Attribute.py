import bpy
from ...base_node import SN_BaseNode


class SN_GetAttributeNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_GetAttributeNode"
    bl_label = "Get Attribute"
