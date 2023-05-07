import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_BlenderPropertyNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_BlenderPropertyNode"
    bl_label = "Blender Property"
