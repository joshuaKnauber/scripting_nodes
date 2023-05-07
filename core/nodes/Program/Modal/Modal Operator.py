import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ModalOperatorNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ModalOperatorNode"
    bl_label = "Modal Operator"
