import bpy
import os
from ..base_node import SN_BaseNode


class SN_IconNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_IconNode"
    bl_label = "Icon"
