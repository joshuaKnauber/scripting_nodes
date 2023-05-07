import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_HasCustomPropertyNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_HasCustomPropertyNode"
    bl_label = "Has Custom Property"
