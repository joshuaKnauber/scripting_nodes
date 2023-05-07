import bpy
from random import uniform
from ..base_node import SN_ScriptingBaseNode


class SN_TimestampNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_TimestampNode"
    bl_label = "Timestamp"
