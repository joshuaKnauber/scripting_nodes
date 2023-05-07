import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_NodeGroupOutputNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_NodeGroupOutputNode"
    bl_label = "Group Output"
    bl_width_min = 200
