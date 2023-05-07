import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_SwitchDataNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_SwitchDataNode"
    bl_label = "Switch Data"
