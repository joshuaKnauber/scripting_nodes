import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_CreateFolderNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_CreateFolderNode"
    bl_label = "Create Folder"
