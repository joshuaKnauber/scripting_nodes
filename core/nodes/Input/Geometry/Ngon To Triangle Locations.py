import bpy
from ...base_node import SN_BaseNode


class SN_NgonToTriangleLocationsNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_NgonToTriangleLocationsNode"
    bl_label = "Ngon To Triangle Locations"
