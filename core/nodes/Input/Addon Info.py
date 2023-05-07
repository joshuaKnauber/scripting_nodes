import bpy
from ..base_node import SN_BaseNode


class SN_AddonInfoNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_AddonInfoNode"
    bl_label = "Addon Info"
