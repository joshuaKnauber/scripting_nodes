import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_EnumMapInterfaceNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_EnumMapInterfaceNode"
    bl_label = "Enum Map (Interface)"
