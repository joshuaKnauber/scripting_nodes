import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_NgonToTriangleLocationsNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_NgonToTriangleLocationsNode"
    bl_label = "Ngon To Triangle Locations"
