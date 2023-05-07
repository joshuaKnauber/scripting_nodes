import bpy
from ..base_node import SN_BaseNode


class SN_RunFunctionNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RunFunctionNode"
    bl_label = "Function Run (Execute)"
