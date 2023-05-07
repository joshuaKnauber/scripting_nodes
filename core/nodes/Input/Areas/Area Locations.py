import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_AreaLocationsNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_AreaLocationsNode"
    bl_label = "Area Locations"
