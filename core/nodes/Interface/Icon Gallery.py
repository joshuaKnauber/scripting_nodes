import bpy
from ..base_node import SN_BaseNode


class SN_IconGalleryNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_IconGalleryNodeNew"
    bl_label = "Icon Gallery"
