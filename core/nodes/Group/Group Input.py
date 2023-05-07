import bpy
from ..base_node import SN_BaseNode


class SN_NodeGroupInputNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_NodeGroupInputNode"
    bl_label = "Group Input"
    bl_width_min = 200
