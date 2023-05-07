import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_BooleanVectorNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_BooleanVectorNode"
    bl_label = "Boolean Vector"
