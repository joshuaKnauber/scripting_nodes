import bpy
from ...base_node import SN_BaseNode


class SN_FloatVectorNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_FloatVectorNode"
    bl_label = "Float Vector"
