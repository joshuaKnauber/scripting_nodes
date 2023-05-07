import bpy
from ..base_node import SN_BaseNode


class SN_NodeGroupOutputNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_NodeGroupOutputNode"
    bl_label = "Group Output"
    bl_width_min = 200
