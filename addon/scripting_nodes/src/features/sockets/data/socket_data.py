from ..base_socket import ScriptingBaseSocket
import bpy


class ScriptingDataSocket(ScriptingBaseSocket, bpy.types.NodeSocket):
    bl_idname = "ScriptingDataSocket"
    bl_label = "Data"

    def _to_code(self):
        return "None"

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    @classmethod
    def draw_color_simple(cls):
        return (0.35, 0.35, 0.35, 1)
