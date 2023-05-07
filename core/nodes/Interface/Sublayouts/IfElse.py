import bpy
from ...base_node import SN_BaseNode


class SN_IfElseInterfaceNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_IfElseInterfaceNodeNew"
    bl_label = "If/Else (Interface)"
