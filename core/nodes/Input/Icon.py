import bpy
import os
from ..base_node import SN_ScriptingBaseNode


class SN_IconNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_IconNode"
    bl_label = "Icon"
