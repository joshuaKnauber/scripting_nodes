import bpy
from ...base_node import SN_BaseNode


class SN_CreateLineLocationsNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_CreateLineLocationsNode"
    bl_label = "Create Line"
