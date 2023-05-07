import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ReportNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ReportNode"
    bl_label = "Report"
