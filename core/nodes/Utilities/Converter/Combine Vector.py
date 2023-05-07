import bpy
import string
from ...base_node import SN_ScriptingBaseNode


class SN_CombineVectorNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_CombineVectorNode"
    bl_label = "Combine Vector"
