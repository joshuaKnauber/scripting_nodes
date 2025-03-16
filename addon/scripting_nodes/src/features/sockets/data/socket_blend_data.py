from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingDataSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingBlendDataSocket"
    bl_label = "Blend Data"

    def _to_code(self):
        return "None"

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    @classmethod
    def draw_color_simple(cls):
        return (0.0, 0.87, 0.7, 1)
