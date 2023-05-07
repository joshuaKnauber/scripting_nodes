import bpy
from ...base_node import SN_BaseNode


class SN_CreateQuadLocationsNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_CreateQuadLocationsNode"
    bl_label = "Create Quad"
