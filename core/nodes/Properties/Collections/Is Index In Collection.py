import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_IsIndexInCollectionPropertyNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_IsIndexInCollectionPropertyNode"
    bl_label = "Is Index In Collection"
