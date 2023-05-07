import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_TriggerNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_TriggerNode"
    bl_label = "Trigger"
