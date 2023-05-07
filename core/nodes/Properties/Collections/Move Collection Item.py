import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_MoveCollectionItemNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_MoveCollectionItemNode"
    bl_label = "Move Collection Item"
