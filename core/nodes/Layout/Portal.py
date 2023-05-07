import bpy
from random import uniform
from ..base_node import SN_BaseNode


class SN_PortalNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_PortalNode"
    bl_label = "Portal"
