import bpy
from ..base_node import SN_BaseNode


class SN_SwitchDataNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SwitchDataNode"
    bl_label = "Switch Data"
