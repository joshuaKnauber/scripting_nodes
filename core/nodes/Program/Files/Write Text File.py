import bpy
from ...base_node import SN_BaseNode


class SN_WriteTextFileNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_WriteTextFileNode"
    bl_label = "Write Text File"
