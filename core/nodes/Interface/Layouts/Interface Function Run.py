import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_RunInterfaceFunctionNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_RunInterfaceFunctionNodeNew"
    bl_label = "Function Run (Interface)"
