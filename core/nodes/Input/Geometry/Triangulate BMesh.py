import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_TriangulateBmeshNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_TriangulateBmeshNode"
    bl_label = "Triangulate BMesh"
