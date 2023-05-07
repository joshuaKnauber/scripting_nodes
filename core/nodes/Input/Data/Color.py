import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ColorNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ColorNode"
    bl_label = "Color"
