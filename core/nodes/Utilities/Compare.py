import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_CompareNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_CompareNode"
    bl_label = "Compare"
