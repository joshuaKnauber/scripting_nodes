import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_DepsgraphUpdateNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_DepsgraphUpdateNode"
    bl_label = "On Depsgraph Update"
