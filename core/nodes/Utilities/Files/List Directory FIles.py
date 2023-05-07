import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_ListDirectoryFilesNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_ListDirectoryFilesNode"
    bl_label = "List Directory Files"
