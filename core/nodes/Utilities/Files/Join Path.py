import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_JoinPathNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_JoinPathNode"
    bl_label = "Join Path"
