import bpy
from ...base_node import SN_BaseNode


class SN_CollectionLengthNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_CollectionLengthNode"
    bl_label = "Collection Length"
