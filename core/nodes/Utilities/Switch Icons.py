import bpy
from ..base_node import SN_BaseNode


class SN_SwitchIconNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_SwitchIconNode"
    bl_label = "Switch Icons"
