import bpy
from ...base_node import SN_BaseNode


class SN_BlenderDataNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_BlenderDataNode"
    bl_label = "Blender Data"
