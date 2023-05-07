import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_NamedIconNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_NamedIconNode"
    bl_label = "Named Icon"
