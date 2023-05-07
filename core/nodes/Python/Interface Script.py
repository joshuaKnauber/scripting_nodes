import bpy
import os
from ..base_node import SN_BaseNode


class SN_InterfaceScriptNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_InterfaceScriptNode"
    bl_label = "Interface Script"
