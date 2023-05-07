import bpy
from ...base_node import SN_BaseNode


class SN_ClampNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ClampNode"
    bl_label = "Clamp"
