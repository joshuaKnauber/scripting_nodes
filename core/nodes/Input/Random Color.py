import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_RandomColorNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_RandomColorNode"
    bl_label = "Random Color"
