import bpy
from ..base_node import SN_BaseNode


class SN_GetDataScriptlineNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_GetDataScriptlineNode"
    bl_label = "Get Data Scriptline"
