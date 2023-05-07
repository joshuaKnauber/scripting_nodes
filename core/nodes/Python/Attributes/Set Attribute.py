import bpy
from ...base_node import SN_BaseNode


class SN_SetAttributeNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SetAttributeNode"
    bl_label = "Set Attribute"
