import bpy
from random import randint
from ...base_node import SN_ScriptingBaseNode


class SN_LofiNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_LofiNode"
    bl_label = "LoFi"
