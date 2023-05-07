import bpy
from ...base_node import SN_BaseNode


class SN_AddCollectionItemNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_AddCollectionItemNode"
    bl_label = "Add Collection Item"
