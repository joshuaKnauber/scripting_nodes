import bpy
from ...base_node import SN_BaseNode


class SN_DataToIconNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_DataToIconNode"
    bl_label = "Data To Icon"
