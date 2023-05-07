import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_SerpensPropertyNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_SerpensPropertyNode"
    bl_label = "Serpens Property"
