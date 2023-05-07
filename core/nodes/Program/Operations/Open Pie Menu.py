import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_OpenPieMenuNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_OpenPieMenuNode"
    bl_label = "Open Pie Menu"
