import bpy
from ...base_node import SN_BaseNode


class SN_CreateTriangleLocationsNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_CreateTriangleLocationsNode"
    bl_label = "Create Triangle"
