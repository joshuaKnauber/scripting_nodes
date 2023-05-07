import bpy
from ...base_node import SN_BaseNode


class SN_RepeatInterfaceNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RepeatInterfaceNodeNew"
    bl_label = "Loop Repeat (Interface)"
