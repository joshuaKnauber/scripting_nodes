import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_SetHeaderTextNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_SetHeaderTextNode"
    bl_label = "Set Header Text"
