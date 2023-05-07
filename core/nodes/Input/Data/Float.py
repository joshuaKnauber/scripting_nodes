import bpy
from ...base_node import SN_BaseNode


class SN_FloatNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_FloatNode"
    bl_label = "Float"
