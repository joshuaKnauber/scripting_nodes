from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingLogicSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingLogicSocket"
    bl_label = "Logic"
    socket_type = "PROGRAM"

    socket_shape = "DIAMOND"

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def _to_code(self):
        pass

    @classmethod
    def draw_color_simple(cls):
        return (1, 1, 1, 1)
