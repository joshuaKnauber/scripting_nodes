import bpy
from ...base_node import SN_BaseNode


class SN_ModalEventNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ModalEventNode"
    bl_label = "Modal Event"
