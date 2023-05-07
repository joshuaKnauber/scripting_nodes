import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_RandomNumberNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_RandomNumberNode"
    bl_label = "Random Number"
