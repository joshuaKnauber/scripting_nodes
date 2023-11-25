import bpy

from ..base_socket import ScriptingSocket


class SNA_DictSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SNA_DictSocket"

    def on_create(self, context: bpy.types.Context):
        self.display_shape = "SQUARE"

    def _python_value(self):
        if self.is_output:
            return self.code if self.code else "{}"
        return "{}"

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (1, 0.49, 0.2, 1)

    def draw_socket(self, context, layout, node, text):
        if not self.is_output:
            if self.show_editable:
                layout.prop(
                    self,
                    "editable",
                    text="",
                    icon="HIDE_OFF" if self.editable else "HIDE_ON",
                    emboss=False,
                )
        layout.label(text=text)
