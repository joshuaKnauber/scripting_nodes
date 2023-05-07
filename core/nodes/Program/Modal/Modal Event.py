import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ModalEventNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ModalEventNode"
    bl_label = "Modal Event"
