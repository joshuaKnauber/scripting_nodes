import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_RegionToViewNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_RegionToViewNode"
    bl_label = "Region To View"
