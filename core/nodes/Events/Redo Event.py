import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_RedoEventNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_RedoEventNode"
    bl_label = "On Redo"
