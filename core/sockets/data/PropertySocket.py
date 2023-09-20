import bpy

from ..base_socket import ScriptingSocket


class SN_PropertySocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SN_PropertySocket"

    def python_value(self):
        return "None"

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (0, 0.87, 0.7, 1)

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)
