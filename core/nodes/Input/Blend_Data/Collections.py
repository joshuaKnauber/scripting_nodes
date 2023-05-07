import bpy
from ...base_node import SN_BaseNode


class SN_CollectionsBlendDataNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_CollectionsBlendDataNode"
    bl_label = "Collections"
