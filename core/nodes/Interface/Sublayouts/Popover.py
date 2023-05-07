import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_PopoverNodeNew(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_PopoverNodeNew"
    bl_label = "Popover"
