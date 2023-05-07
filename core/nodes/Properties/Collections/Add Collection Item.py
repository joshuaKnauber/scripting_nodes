import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_AddCollectionItemNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_AddCollectionItemNode"
    bl_label = "Add Collection Item"
