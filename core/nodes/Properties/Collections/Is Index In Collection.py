import bpy
from ...base_node import SN_BaseNode


class SN_IsIndexInCollectionPropertyNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_IsIndexInCollectionPropertyNode"
    bl_label = "Is Index In Collection"
