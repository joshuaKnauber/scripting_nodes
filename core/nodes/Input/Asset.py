import bpy
import os
from ..base_node import SN_BaseNode


class SN_AssetNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_AssetNode"
    bl_label = "Asset"
