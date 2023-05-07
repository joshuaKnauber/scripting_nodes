import bpy
from ..base_node import SN_BaseNode


class SN_DisplayCollectionListNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_DisplayCollectionListNodeNew"
    bl_label = "Display Collection List"
