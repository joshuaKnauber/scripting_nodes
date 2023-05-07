import bpy
from ...base_node import SN_BaseNode


class SN_PopoverNodeNew(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_PopoverNodeNew"
    bl_label = "Popover"
