import re
import bpy
import string
from ...base_node import SN_BaseNode


class SN_MathNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_MathNode"
    bl_label = "Math"
