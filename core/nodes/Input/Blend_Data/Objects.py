import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ObjectBlendDataNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ObjectBlendDataNode"
    bl_label = "Objects"
