import bpy
from ..base_node import SN_BaseNode


class SN_InterfaceScriptlineNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_InterfaceScriptlineNode"
    bl_label = "Interface Scriptline"
