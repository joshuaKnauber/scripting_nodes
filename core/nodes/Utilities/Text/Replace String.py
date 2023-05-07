import bpy
from ...base_node import SN_BaseNode


class SN_ReplaceStringNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ReplaceStringNode"
    bl_label = "Replace in String"
