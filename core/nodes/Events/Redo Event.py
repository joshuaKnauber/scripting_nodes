import bpy
from ..base_node import SN_BaseNode


class SN_RedoEventNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_RedoEventNode"
    bl_label = "On Redo"
