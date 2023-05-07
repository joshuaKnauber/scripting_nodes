import bpy
from ...base_node import SN_ScriptingBaseNode


class SN_CollectionsBlendDataNode(SN_ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SN_CollectionsBlendDataNode"
    bl_label = "Collections"
