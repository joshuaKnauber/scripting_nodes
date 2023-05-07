import bpy
from ...base_node import SN_BaseNode


class SN_AreaByTypeNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_AreaByTypeNode"
    bl_label = "Area By Type"
