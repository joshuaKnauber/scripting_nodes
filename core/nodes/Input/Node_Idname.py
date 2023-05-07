import bpy
from ..base_node import SN_BaseNode


class SN_NodeIdnameNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_NodeIdnameNode"
    bl_label = "Node Idname"
