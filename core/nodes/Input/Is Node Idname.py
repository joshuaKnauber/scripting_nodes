import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_NodeIsIdname(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_NodeIsIdname"
    bl_label = "Node Is Idname"
