import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_BooleanNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_BooleanNode"
    bl_label = "Boolean"
