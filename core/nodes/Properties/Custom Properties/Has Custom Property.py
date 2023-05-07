import bpy
from ...base_node import SN_BaseNode


class SN_HasCustomPropertyNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_HasCustomPropertyNode"
    bl_label = "Has Custom Property"
