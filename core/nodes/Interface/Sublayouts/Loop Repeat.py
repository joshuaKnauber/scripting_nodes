import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_RepeatInterfaceNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_RepeatInterfaceNodeNew"
    bl_label = "Loop Repeat (Interface)"
