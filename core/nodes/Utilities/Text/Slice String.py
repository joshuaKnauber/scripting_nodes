import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_SliceStringNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_SliceStringNode"
    bl_label = "Slice String"
