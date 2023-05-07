import bpy
from ..base_node import SN_BaseNode


class SN_LabelNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_LabelNodeNew"
    bl_label = "Label"
