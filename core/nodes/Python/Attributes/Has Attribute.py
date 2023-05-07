import bpy
from ...base_node import SN_BaseNode


class SN_HasAttributeNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_HasAttributeNode"
    bl_label = "Has Attribute"
