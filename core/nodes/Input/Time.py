import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_TimeNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_TimeNode"
    bl_label = "Time and Date"
