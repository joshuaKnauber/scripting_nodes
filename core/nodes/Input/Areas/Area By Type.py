import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_AreaByTypeNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_AreaByTypeNode"
    bl_label = "Area By Type"
