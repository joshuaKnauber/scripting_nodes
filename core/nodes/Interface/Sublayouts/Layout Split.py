import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_LayoutSplitNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_LayoutSplitNodeNew"
    bl_label = "Split"
