import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_RemoveCollectionItemNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_RemoveCollectionItemNode"
    bl_label = "Remove Collection Item"
