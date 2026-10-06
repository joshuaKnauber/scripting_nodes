from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingBlendDataSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingBlendDataSocket"
    bl_label = "Blend Data"

    def _to_code(self):
        return "None"

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)

    @classmethod
    def draw_color_simple(cls):
        # Teal color
        return (0.0, 0.75, 0.65, 1)
