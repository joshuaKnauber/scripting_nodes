import bpy
from ..base_node import SN_BaseNode


class SN_BeforeExitNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_BeforeExitNode"
    bl_label = "On Blender Close"
