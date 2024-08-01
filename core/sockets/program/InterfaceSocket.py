from typing import Any
import bpy
from bpy.types import Context, Node, NodeSocket, UILayout

from ..base_socket import ScriptingSocket


class SNA_InterfaceSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SNA_InterfaceSocket"
    bl_label = "Interface"
    is_program = True

    def on_create(self, context: bpy.types.Context):
        self.display_shape = "DIAMOND"

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (0.9, 0.6, 0, 1)

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)


class SNA_InterfaceSocketInterface(bpy.types.NodeTreeInterfaceSocket):

    bl_idname = "SNA_InterfaceSocketInterface"
    bl_socket_idname = "SNA_InterfaceSocket"
    bl_label = "Interface"

    def draw(self, context: Context, layout: UILayout):
        pass


def register():
    bpy.utils.register_class(SNA_InterfaceSocketInterface)


def unregister():
    bpy.utils.unregister_class(SNA_InterfaceSocketInterface)
