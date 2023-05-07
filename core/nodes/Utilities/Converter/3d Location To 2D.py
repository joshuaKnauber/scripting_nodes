import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_3DLocationTo2DNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_3DLocationTo2DNode"
    bl_label = "3D View Coordinates To 2D"
