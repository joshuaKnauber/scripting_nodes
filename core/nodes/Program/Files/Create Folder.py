import bpy
from ...base_node import SN_BaseNode


class SN_CreateFolderNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_CreateFolderNode"
    bl_label = "Create Folder"
