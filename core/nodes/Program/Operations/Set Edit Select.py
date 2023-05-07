import bpy
from ...base_node import SN_BaseNode


class SN_SetEditSelectNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SetEditSelectNode"
    bl_label = "Set Edit Select"
