from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingProgramSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingProgramSocket"
    bl_label = "Program"
    socket_type = "PROGRAM"

    socket_shape = "DIAMOND"

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def _to_code(self):
        pass

    @classmethod
    def draw_color_simple(cls):
        return (0.3, 0.3, 0.3, 1)
