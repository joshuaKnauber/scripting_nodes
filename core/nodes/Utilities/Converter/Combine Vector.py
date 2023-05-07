import bpy
import string
from ...base_node import SN_BaseNode


class SN_CombineVectorNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_CombineVectorNode"
    bl_label = "Combine Vector"
