import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ViewToRegionNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ViewToRegionNode"
    bl_label = "View To Region"
