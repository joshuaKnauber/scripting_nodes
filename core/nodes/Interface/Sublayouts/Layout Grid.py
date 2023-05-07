import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_LayoutGridNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_LayoutGridNode"
    bl_label = "Grid"
