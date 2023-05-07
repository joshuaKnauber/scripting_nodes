import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_IndexCollectionPropertyNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_IndexCollectionPropertyNode"
    bl_label = "Index Collection Property"
