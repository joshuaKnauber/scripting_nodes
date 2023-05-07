import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_IfElseInterfaceNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_IfElseInterfaceNodeNew"
    bl_label = "If/Else (Interface)"
