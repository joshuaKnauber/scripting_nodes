import bpy
from ...base_node import SN_BaseNode


class SN_StripStringNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_StripStringNode"
    bl_label = "Strip String"
