import bpy
from ..base_socket import ScriptingSocket


class SN_ExecuteSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_ExecuteSocket"
    is_program = True

    def on_create(self, context):
        self.display_shape = "DIAMOND"

    def get_color(self, context, node):
        return (1, 1, 1)
