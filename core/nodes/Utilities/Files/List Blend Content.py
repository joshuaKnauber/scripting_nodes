import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ListBlendContentNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ListBlendContentNode"
    bl_label = "List Blend File Content"
