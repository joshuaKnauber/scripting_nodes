import bpy
from ..base_node import SN_BaseNode


class SN_NamedIconNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_NamedIconNode"
    bl_label = "Named Icon"
