import bpy
from ...base_node import SN_BaseNode


class SN_SetCustomPropertyNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SetCustomPropertyNode"
    bl_label = "Set Custom Property"
