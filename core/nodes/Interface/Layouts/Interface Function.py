import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_InterfaceFunctionNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_InterfaceFunctionNode"
    bl_label = "Function (Interface)"
