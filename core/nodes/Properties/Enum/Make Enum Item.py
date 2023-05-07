import bpy
from ...base_node import SN_BaseNode


class SN_MakeEnumItemNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_MakeEnumItemNode"
    bl_label = "Make Enum Item"
