import bpy
from ..base_node import SN_BaseNode


class SN_GetPropertyScriptlineNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_GetPropertyScriptlineNode"
    bl_label = "Get Property Scriptline"
