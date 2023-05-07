import bpy
from ...base_node import SN_BaseNode


class SN_AppendFromFileNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_AppendFromFileNode"
    bl_label = "Append From File"
