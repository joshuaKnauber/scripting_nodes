import bpy
from ...base_node import SN_BaseNode


class SN_InvertBooleanNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_InvertBooleanNode"
    bl_label = "Invert Boolean"
