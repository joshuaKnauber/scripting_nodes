import bpy
from ...base_node import SN_BaseNode


class SN_MoveCollectionItemNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_MoveCollectionItemNode"
    bl_label = "Move Collection Item"
