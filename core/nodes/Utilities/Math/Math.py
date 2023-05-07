import re
import bpy
import string
from ...base_node import SN_ScriptingBaseNode


class SN_MathNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_MathNode"
    bl_label = "Math"
