import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_CreateLineLocationsNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_CreateLineLocationsNode"
    bl_label = "Create Line"
