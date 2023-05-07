import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_AddonInfoNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_AddonInfoNode"
    bl_label = "Addon Info"
