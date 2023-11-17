import bpy

from ..base_socket import ScriptingSocket


class SNA_ExecuteSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SNA_ExecuteSocket"
    is_program = True

    def on_create(self, context: bpy.types.Context):
        self.display_shape = "DIAMOND"

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (1, 1, 1, 1)

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)
