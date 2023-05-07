import bpy
from ..base_node import SN_BaseNode


class SN_RunPropertyFunctionNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RunPropertyFunctionNode"
    bl_label = "Run Property Function"
