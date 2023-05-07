import bpy
from ...base_node import SN_BaseNode


class SN_DrawQuadNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_DrawQuadNode"
    bl_label = "Draw Quad"
