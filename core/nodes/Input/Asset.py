import bpy
import os
from ..base_node import SN_ScriptingBaseNode


class SN_AssetNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_AssetNode"
    bl_label = "Asset"
