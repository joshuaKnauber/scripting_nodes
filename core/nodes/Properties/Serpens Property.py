import bpy
from ..base_node import SN_BaseNode


class SN_SerpensPropertyNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SerpensPropertyNode"
    bl_label = "Serpens Property"
