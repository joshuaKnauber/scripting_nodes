import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_RadiansNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_RadiansNode"
    bl_label = "Convert Radians/Degrees"
