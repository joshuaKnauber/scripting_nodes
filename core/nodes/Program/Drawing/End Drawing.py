import bpy
from ...base_node import SN_BaseNode


class SN_EndDrawingNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_EndDrawingNode"
    bl_label = "End Drawing"
