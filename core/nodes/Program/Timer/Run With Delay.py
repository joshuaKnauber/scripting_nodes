import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_RunWithDelayNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_RunWithDelayNode"
    bl_label = "Run With Delay"
