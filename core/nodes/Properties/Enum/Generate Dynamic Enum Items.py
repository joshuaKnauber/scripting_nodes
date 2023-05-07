import bpy
from ...base_node import SN_BaseNode


class SN_GenerateEnumItemsNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_GenerateEnumItemsNode"
    bl_label = "Generate Dynamic Enum Items"
