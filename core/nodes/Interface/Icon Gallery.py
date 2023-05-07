import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_IconGalleryNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_IconGalleryNodeNew"
    bl_label = "Icon Gallery"
