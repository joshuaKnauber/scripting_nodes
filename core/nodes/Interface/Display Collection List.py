import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_DisplayCollectionListNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_DisplayCollectionListNodeNew"
    bl_label = "Display Collection List"
