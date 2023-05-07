import bpy
from ..base_socket import ScriptingSocket


class SN_InterfaceSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_InterfaceSocket"
    is_program = True

    def on_create(self, context):
        self.display_shape = "DIAMOND"

    def get_color(self, context, node):
        return (0.9, 0.6, 0)
