import bpy
from random import randint
from ...base_node import SN_BaseNode


class SN_LofiNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_LofiNode"
    bl_label = "LoFi"
