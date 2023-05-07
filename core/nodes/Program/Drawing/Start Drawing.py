import bpy
from ...base_node import SN_BaseNode


class SN_StartDrawingNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_StartDrawingNode"
    bl_label = "Start Drawing"
