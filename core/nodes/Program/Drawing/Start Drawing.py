import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_StartDrawingNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_StartDrawingNode"
    bl_label = "Start Drawing"
