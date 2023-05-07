import bpy
from ..base_node import SN_BaseNode


class SN_SetPropertyNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SetPropertyNode"
    bl_label = "Set Property"
