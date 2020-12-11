import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_TestNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_TestNode"
    bl_label = "Test"
    bl_icon = "GRAPH"