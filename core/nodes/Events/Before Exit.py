import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_BeforeExitNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_BeforeExitNode"
    bl_label = "On Blender Close"
