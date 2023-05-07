import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_BlenderDataNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_BlenderDataNode"
    bl_label = "Blender Data"
