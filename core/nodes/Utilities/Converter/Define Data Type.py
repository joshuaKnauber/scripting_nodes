import bpy
from ...base_node import SN_BaseNode


class SN_DefineDataType(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_DefineDataType"
    bl_label = "Define Data Type"
