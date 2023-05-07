import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_AddToPanelNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_AddToPanelNodeNew"
    bl_label = "Add To Panel"
