import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_EnumSetToListNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_EnumSetToListNode"
    bl_label = "Enum Set To List"
