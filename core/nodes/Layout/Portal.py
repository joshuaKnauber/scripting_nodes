import bpy
from random import uniform
from ..base_node import SN_ScriptingBaseNode


class SN_PortalNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_PortalNode"
    bl_label = "Portal"
