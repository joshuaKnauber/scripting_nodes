import bpy
from ...base_node import SN_BaseNode


class SN_ReadTextFileNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ReadTextFileNode"
    bl_label = "Read Text File"
