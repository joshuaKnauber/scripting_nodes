import bpy
from ...base_node import SN_BaseNode


class SN_JoinPathNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_JoinPathNode"
    bl_label = "Join Path"
