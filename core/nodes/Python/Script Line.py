import bpy
from ..base_node import SN_BaseNode


class SN_ScriptlineNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ScriptlineNode"
    bl_label = "Scriptline"
