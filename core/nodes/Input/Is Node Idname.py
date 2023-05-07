import bpy
from ..base_node import SN_BaseNode


class SN_NodeIsIdname(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_NodeIsIdname"
    bl_label = "Node Is Idname"
