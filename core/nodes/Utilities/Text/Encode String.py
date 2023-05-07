import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_EncodeStringNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_EncodeStringNode"
    bl_label = "Encode Byte String"
