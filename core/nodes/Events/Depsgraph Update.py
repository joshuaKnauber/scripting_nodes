import bpy
from ..base_node import SN_BaseNode


class SN_DepsgraphUpdateNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_DepsgraphUpdateNode"
    bl_label = "On Depsgraph Update"
