import bpy
from ...base_node import SN_BaseNode


class SN_GetCustomPropertyNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_GetCustomPropertyNode"
    bl_label = "Get Custom Property"
