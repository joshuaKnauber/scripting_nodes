import bpy
from ..base_node import SN_BaseNode


class SN_UndoEventNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_UndoEventNode"
    bl_label = "On Undo"
