import bpy
from ..base_node import SN_BaseNode


class SN_OnSaveNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_OnSaveNode"
    bl_label = "On Save"
