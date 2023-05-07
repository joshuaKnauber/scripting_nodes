import bpy
from ..base_node import SN_BaseNode


class SN_PropertyExistsNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_PropertyExistsNode"
    bl_label = "Property Exists"
