import bpy
from ...base_node import SN_BaseNode


class SN_RepeatExecuteNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RepeatExecuteNode"
    bl_label = "Loop Repeat (Execute)"
