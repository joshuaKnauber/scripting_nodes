import bpy
from ...base_node import SN_BaseNode


class SN_RemoveCollectionItemNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RemoveCollectionItemNode"
    bl_label = "Remove Collection Item"
