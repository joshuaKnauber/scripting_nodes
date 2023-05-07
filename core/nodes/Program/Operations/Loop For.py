import bpy
from ...base_node import SN_BaseNode


class SN_ForExecuteNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ForExecuteNode"
    bl_label = "Loop For (Execute)"
