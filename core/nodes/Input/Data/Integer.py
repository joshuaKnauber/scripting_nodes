import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_IntegerNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_IntegerNode"
    bl_label = "Integer"
