import bpy
from ...base_node import SN_BaseNode


class SN_ReportNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ReportNode"
    bl_label = "Report"
