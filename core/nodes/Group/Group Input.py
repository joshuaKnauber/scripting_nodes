import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_NodeGroupInputNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_NodeGroupInputNode"
    bl_label = "Group Input"
    bl_width_min = 200
