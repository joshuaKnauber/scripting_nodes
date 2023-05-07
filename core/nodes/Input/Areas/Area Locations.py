import bpy
from ...base_node import SN_BaseNode


class SN_AreaLocationsNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_AreaLocationsNode"
    bl_label = "Area Locations"
