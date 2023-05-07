import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_IntegerVectorNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_IntegerVectorNode"
    bl_label = "Integer Vector"
