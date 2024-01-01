import bpy
from ..base_node import SNA_BaseNode


class SNA_NodeGroupOutputNode(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeGroupOutputNode"
    bl_label = "Group Output"
    bl_width_min = 200
