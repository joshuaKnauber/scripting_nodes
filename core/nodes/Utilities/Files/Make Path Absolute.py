import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_AbsolutePathNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_AbsolutePathNode"
    bl_label = "Make Path Absolute"
