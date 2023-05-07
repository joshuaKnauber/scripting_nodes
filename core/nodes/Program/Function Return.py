import bpy
from ..base_node import SN_BaseNode


class SN_FunctionReturnNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_FunctionReturnNode"
    bl_label = "Function Return (Execute)"
