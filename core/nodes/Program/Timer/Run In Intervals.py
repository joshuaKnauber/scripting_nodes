import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_RunInIntervalsNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_RunInIntervalsNode"
    bl_label = "Run In Intervals"
