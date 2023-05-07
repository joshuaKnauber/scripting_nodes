import bpy
from ...base_node import SN_BaseNode


class SN_RunMultipleTimesNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RunMultipleTimesNode"
    bl_label = "Run Multiple Times"
