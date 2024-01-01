import bpy
from ..base_node import SNA_BaseNode


class SNA_NodeGroupInputNode(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeGroupInputNode"
    bl_label = "Group Input"
    bl_width_min = 200
