import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_LabelNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_LabelNodeNew"
    bl_label = "Label"
