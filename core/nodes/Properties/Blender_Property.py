import bpy
from ..base_node import SN_BaseNode


class SN_BlenderPropertyNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_BlenderPropertyNode"
    bl_label = "Blender Property"
