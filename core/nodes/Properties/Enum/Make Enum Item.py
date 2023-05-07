import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_MakeEnumItemNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_MakeEnumItemNode"
    bl_label = "Make Enum Item"
