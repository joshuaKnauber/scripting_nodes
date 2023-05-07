import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_LayoutBoxNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_LayoutBoxNodeNew"
    bl_label = "Box"
