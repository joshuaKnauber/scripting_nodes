import bpy
from ...base_node import SN_BaseNode


class SN_ObjectBlendDataNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ObjectBlendDataNode"
    bl_label = "Objects"
