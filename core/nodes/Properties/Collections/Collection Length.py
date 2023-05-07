import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_CollectionLengthNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_CollectionLengthNode"
    bl_label = "Collection Length"
