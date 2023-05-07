import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_PadStringNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_PadStringNode"
    bl_label = "Pad String"
