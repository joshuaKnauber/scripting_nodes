import bpy
from ...base_node import SN_BaseNode


class SN_IndexListNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_IndexListNode"
    bl_label = "Index List"
