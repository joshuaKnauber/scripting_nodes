import bpy
import os
from ..base_node import SN_ScriptingBaseNode


class SN_InterfaceScriptNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_InterfaceScriptNode"
    bl_label = "Interface Script"
