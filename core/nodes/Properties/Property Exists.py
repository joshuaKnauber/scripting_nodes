import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_PropertyExistsNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_PropertyExistsNode"
    bl_label = "Property Exists"
