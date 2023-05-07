import bpy
from ..base_node import SN_BaseNode


class SN_FunctionNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_FunctionNode"
    bl_label = "Function (Execute)"
