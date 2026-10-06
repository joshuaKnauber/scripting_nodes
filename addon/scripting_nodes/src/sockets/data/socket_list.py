from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingListSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingListSocket"
    bl_label = "List"

    socket_shape = "SQUARE"

    def _to_code(self):
        return "[]"

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)

    @classmethod
    def draw_color_simple(cls):
        return (0.8, 0.5, 0.2, 1)
