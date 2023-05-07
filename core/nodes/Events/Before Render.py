import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_BeforeRenderNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_BeforeRenderNode"
    bl_label = "On Render Start"
