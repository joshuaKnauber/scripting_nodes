import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_DecodeStringNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_DecodeStringNode"
    bl_label = "Decode Byte String"
