import bpy
from ...base_node import SN_BaseNode


class SN_RunInterfaceFunctionNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RunInterfaceFunctionNodeNew"
    bl_label = "Function Run (Interface)"
