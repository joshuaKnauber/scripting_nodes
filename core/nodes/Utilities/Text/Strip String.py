import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_StripStringNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_StripStringNode"
    bl_label = "Strip String"
