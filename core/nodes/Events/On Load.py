import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_OnLoadNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_OnLoadNode"
    bl_label = "On Load"
