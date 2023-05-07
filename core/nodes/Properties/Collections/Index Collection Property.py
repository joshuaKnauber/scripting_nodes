import bpy
from ...base_node import SN_BaseNode


class SN_IndexCollectionPropertyNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_IndexCollectionPropertyNode"
    bl_label = "Index Collection Property"
