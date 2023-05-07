import bpy
from ...base_node import SN_BaseNode


class SN_ListDirectoryFilesNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_ListDirectoryFilesNode"
    bl_label = "List Directory Files"
