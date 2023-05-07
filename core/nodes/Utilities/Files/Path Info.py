import bpy
from ...base_node import SN_BaseNode


class SN_PathInfoNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_PathInfoNode"
    bl_label = "Path Info"
