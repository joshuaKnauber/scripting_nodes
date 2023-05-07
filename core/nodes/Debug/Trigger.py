import bpy
from ..base_node import SN_BaseNode


class SN_TriggerNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_TriggerNode"
    bl_label = "Trigger"
