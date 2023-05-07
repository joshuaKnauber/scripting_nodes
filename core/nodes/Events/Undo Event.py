import bpy
from ..base_node import SN_ScriptingBaseNode


class SN_UndoEventNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_UndoEventNode"
    bl_label = "On Undo"
