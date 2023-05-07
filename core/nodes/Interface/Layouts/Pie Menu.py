import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_PieMenuNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_PieMenuNode"
    bl_label = "Pie Menu"
