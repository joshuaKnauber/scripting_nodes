import bpy
from ..base_node import SN_BaseNode


class SN_ChangeVariableByNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ChangeVariableByNode"
    bl_label = "Change Variable By"
