import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ForInterfaceNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ForInterfaceNodeNew"
    bl_label = "Loop For (Interface)"
