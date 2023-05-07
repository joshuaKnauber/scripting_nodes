import bpy
from ...base_node import SN_BaseNode


class SN_InterfaceFunctionNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_InterfaceFunctionNode"
    bl_label = "Function (Interface)"
