import bpy
from ..base_node import SN_BaseNode


class SN_RunOperatorNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RunOperatorNode"
    bl_label = "Run Operator"
