import bpy
from ...base_node import SN_BaseNode


class SN_PadStringNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_PadStringNode"
    bl_label = "Pad String"
