import bpy

from ..base_socket import ScriptingSocket


class SN_InterfaceSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_InterfaceSocket"

    def on_create(self, context: bpy.types.Context):
        self.display_shape = "DIAMOND"

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (0.9, 0.6, 0, 1)
