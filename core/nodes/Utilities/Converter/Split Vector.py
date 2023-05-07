import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_SplitVectorNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_SplitVectorNode"
    bl_label = "Split Vector"
