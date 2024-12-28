from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingInterfaceSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingInterfaceSocket"
    bl_label = "Interface"
    socket_type = "PROGRAM"

    socket_shape = "DIAMOND"

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def _to_code(self):
        pass

    @classmethod
    def draw_color_simple(cls):
        return (0.95, 0.65, 0, 1)
