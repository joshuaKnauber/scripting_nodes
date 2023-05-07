import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_PathInfoNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_PathInfoNode"
    bl_label = "Path Info"
