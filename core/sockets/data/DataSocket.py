import bpy

from ..base_socket import ScriptingSocket


class SNA_DataSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_idname = "SNA_DataSocket"
    bl_label = "Data"

    def _python_value(self):
        if self.is_output:
            return self.code if self.code else "None"
        return "None"

    def get_color(self, context: bpy.types.Context, node: bpy.types.Node):
        return (0.2, 0.2, 0.2, 1)

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
